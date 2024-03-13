# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend cache functionality.

Author(s): Alec Delaney
"""

import pathlib
import shutil

import pytest

import circfirm.backend.cache


def test_get_board_folder() -> None:
    """Tests getting UF2 information."""
    board_id = "feather_m4_express"
    board_path = circfirm.backend.cache.get_board_folder(board_id)
    expected_path = pathlib.Path(circfirm.UF2_ARCHIVE) / board_id
    assert board_path.resolve() == expected_path.resolve()


def test_get_uf2_filepath() -> None:
    """Tests getting the UF2 filepath."""
    board_id = "feather_m4_express"
    language = "en_US"
    version = "7.0.0"

    created_path = circfirm.backend.cache.get_uf2_filepath(
        "feather_m4_express", "7.0.0", "en_US"
    )
    expected_path = (
        pathlib.Path(circfirm.UF2_ARCHIVE)
        / board_id
        / f"adafruit-circuitpython-{board_id}-{language}-{version}.uf2"
    )
    assert created_path.resolve() == expected_path.resolve()


def test_download_uf2() -> None:
    """Tests the UF2 download functionality."""
    board_id = "feather_m4_express"
    language = "en_US"
    version = "junktext"

    # Test bad download candidate
    expected_path = (
        circfirm.backend.cache.get_board_folder(board_id)
        / f"adafruit-circuitpython-{board_id}-{language}-{version}.uf2"
    )
    with pytest.raises(ConnectionError):
        circfirm.backend.cache.download_uf2(board_id, version, language)
    assert not expected_path.exists()
    assert not expected_path.parent.exists()

    # Test good download candidate
    assert not circfirm.backend.cache.is_downloaded(board_id, version)
    version = "7.0.0"
    circfirm.backend.cache.download_uf2(board_id, version, language)
    expected_path = (
        circfirm.backend.cache.get_board_folder(board_id)
        / f"adafruit-circuitpython-{board_id}-{language}-{version}.uf2"
    )
    assert expected_path.exists()
    assert circfirm.backend.cache.is_downloaded(board_id, version)

    # Clean up post tests
    shutil.rmtree(expected_path.parent)


def test_parse_firmware_info() -> None:
    """Tests the ability to get firmware information."""
    board_id = "feather_m4_express"
    language = "en_US"

    # Test successful parsing
    for version in ("8.0.0", "9.0.0-beta.2"):
        try:
            board_folder = circfirm.backend.cache.get_board_folder(board_id)
            circfirm.backend.cache.download_uf2(board_id, version, language)
            downloaded_filename = [file.name for file in board_folder.glob("*")][0]

            (
                parsed_version,
                parsed_language,
            ) = circfirm.backend.cache.parse_firmware_info(downloaded_filename)
            assert parsed_version == version
            assert parsed_language == language
        finally:
            # Clean up post tests
            shutil.rmtree(board_folder)

    # Test failed parsing
    with pytest.raises(ValueError):
        circfirm.backend.cache.parse_firmware_info("cannotparse")
