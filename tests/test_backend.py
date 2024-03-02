# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend functionality.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil

import pytest

import circfirm.backend
import tests.helpers


def test_find_circuitpy() -> None:
    """Tests finding a CircuitPython device."""
    # Test when boot_out.txt is preset
    boot_out = tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE)
    tests.helpers.touch_mount_node(boot_out)

    mount_location = tests.helpers.get_mount()
    circuitpy = circfirm.backend.find_circuitpy()
    assert circuitpy == mount_location

    # Test when boot_out.txt is absent
    os.remove(boot_out)
    circuitpy = circfirm.backend.find_circuitpy()
    assert circuitpy is None


def test_find_bootloader() -> None:
    """Tests finding a CircuitPython device in bootloader mode."""
    # Test when info_uf2.txt is preset
    mount_location = tests.helpers.get_mount()
    bootloader = circfirm.backend.find_bootloader()
    assert bootloader == mount_location

    # Test when info_uf2.txt is absent
    uf2_info = tests.helpers.get_mount_node(circfirm.UF2INFO_FILE, True)
    os.remove(uf2_info)
    bootloader = circfirm.backend.find_bootloader()
    assert bootloader is None
    tests.helpers.copy_uf2_info()


def test_get_board_name() -> None:
    """Tests getting the board name from the UF2 info file."""
    # Setup
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    tests.helpers.copy_boot_out()

    # Test successful parsing
    mount_location = tests.helpers.get_mount()
    board_name = circfirm.backend.get_board_name(mount_location)
    assert board_name == "feather_m4_express"

    # Test unsuccessful parsing
    with open(
        tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE), mode="w", encoding="utf-8"
    ) as bootfile:
        bootfile.write("junktext")
    with pytest.raises(ValueError):
        circfirm.backend.get_board_name(mount_location)

    # Clean up
    tests.helpers.delete_mount_node(circfirm.BOOTOUT_FILE)
    tests.helpers.copy_uf2_info()


def test_get_board_folder() -> None:
    """Tests getting UF2 information."""
    board_name = "feather_m4_express"
    board_path = circfirm.backend.get_board_folder(board_name)
    expected_path = pathlib.Path(circfirm.UF2_ARCHIVE) / board_name
    assert board_path.resolve() == expected_path.resolve()


def test_get_uf2_filepath() -> None:
    """Tests getting the UF2 filepath."""
    board_name = "feather_m4_express"
    language = "en_US"
    version = "7.0.0"

    created_path = circfirm.backend.get_uf2_filepath(
        "feather_m4_express", "7.0.0", "en_US", ensure=True
    )
    expected_path = (
        pathlib.Path(circfirm.UF2_ARCHIVE)
        / board_name
        / f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"
    )
    assert created_path.resolve() == expected_path.resolve()


def test_download_uf2() -> None:
    """Tests the UF2 download functionality."""
    board_name = "feather_m4_express"
    language = "en_US"
    version = "junktext"

    # Test bad download candidate
    expected_path = (
        circfirm.backend.get_board_folder(board_name)
        / f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"
    )
    with pytest.raises(ConnectionError):
        circfirm.backend.download_uf2(board_name, version, language)
    assert not expected_path.exists()
    assert not expected_path.parent.exists()

    # Test good download candidate
    assert not circfirm.backend.is_downloaded(board_name, version)
    version = "7.0.0"
    circfirm.backend.download_uf2(board_name, version, language)
    expected_path = (
        circfirm.backend.get_board_folder(board_name)
        / f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"
    )
    assert expected_path.exists()
    assert circfirm.backend.is_downloaded(board_name, version)

    # Clean up post tests
    shutil.rmtree(expected_path.parent)


def test_get_firmware_info() -> None:
    """Tests the ability to get firmware information."""
    board_name = "feather_m4_express"
    language = "en_US"

    # Test successful parsing
    for version in ("8.0.0", "9.0.0-beta.2"):
        try:
            board_folder = circfirm.backend.get_board_folder(board_name)
            circfirm.backend.download_uf2(board_name, version, language)
            downloaded_filename = [file.name for file in board_folder.glob("*")][0]

            parsed_version, parsed_language = circfirm.backend.get_firmware_info(
                downloaded_filename
            )
            assert parsed_version == version
            assert parsed_language == language
        finally:
            # Clean up post tests
            shutil.rmtree(board_folder)

    # Test failed parsing
    with pytest.raises(ValueError):
        circfirm.backend.get_firmware_info("cannotparse")


def test_get_board_list() -> None:
    """Tests the ability of the backend to get the board list."""
    # Test successful retrieval
    token = os.environ["GH_TOKEN"]
    board_list = circfirm.backend.get_board_list(token)
    expected_board_list = tests.helpers.get_boards_from_git()
    assert board_list == expected_board_list

    # Test unsuccessful retrieval
    with pytest.raises(ValueError):
        circfirm.backend.get_board_list("badtoken")


def test_get_rate_limit() -> None:
    """Tests getting the rate limit for an authenticated GitHub request."""
    available, total, reset_time = circfirm.backend.get_rate_limit()
    total_rate_limit = 60
    assert available <= total
    assert total == total_rate_limit
    assert reset_time


def test_get_board_versions() -> None:
    """Tests getting firmware versions for a given board."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_versions = [
        "6.2.0-beta.2",
        "6.2.0-beta.1",
        "6.2.0-beta.0",
    ]
    versions = circfirm.backend.get_board_versions(board, language)
    assert versions == expected_versions

    # Chck that invalid versions are skipped for code coverage
    _ = circfirm.backend.get_board_versions(board, regex=r".*")
