# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for update command.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
import time

from click.testing import CliRunner
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

import circfirm
import circfirm.backend.cache
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()

VERSION = "8.0.0-beta.6"
ORIGINAL_VERSION = "6.0.0"
INCOMPARABLE_VERSION = "7.1.2-rc.0-3-gd897c15f24-dirty"

ERR_IN_BOOTLOADER = 3


def test_update(mock_with_circuitpy: None) -> None:
    """Test the update command when in CIRCUITPY mode."""
    try:
        tests.helpers.set_firmware_version(ORIGINAL_VERSION)
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["update", "--language", "cs"])

        expected_version = "6.1.0"
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", expected_version, language="cs"
        )
        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert result.exit_code == 0
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_update_bad_version_parsing(mock_with_circuitpy: None) -> None:
    """Test the update command when the board has a version that cannot be compareed."""
    tests.helpers.set_firmware_version(INCOMPARABLE_VERSION)
    tests.helpers.start_bootloader_copy_thread()

    result = RUNNER.invoke(cli, ["update", "--language", "cs"])
    assert result.exit_code != 0
    assert result.output == (
        "Board ID detected, please switch the device to bootloader mode.\n"
        f"Board currently has version {INCOMPARABLE_VERSION}, which cannot be used for version comparison.\n"
        "Please use the install command to explicitly install a specific version.\n"
    )

    expected_version = "6.1.0"
    expected_uf2_filename = circfirm.backend.get_uf2_filename(
        "feather_m4_express", expected_version, language="cs"
    )
    expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
    assert not os.path.exists(expected_uf2_filepath)


def test_update_no_internet(mock_no_internet: None, mock_with_circuitpy: None) -> None:
    """Test the update command when in CIRCUITPY mode."""
    try:
        tests.helpers.set_firmware_version(ORIGINAL_VERSION)
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["update", "--language", "cs"])
        assert result.exit_code != 0

        expected_version = "6.1.0"
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", expected_version, language="cs"
        )
        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert not os.path.exists(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():  # pragma: no cover
            shutil.rmtree(board_folder)


def test_update_pre_release(mock_with_circuitpy: None) -> None:
    """Tests the update command when in CIRCUITPY mode with the pre-release flag."""
    try:
        tests.helpers.set_firmware_version(ORIGINAL_VERSION)
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["update", "--language", "cs", "--pre-release"])

        expected_version = "6.2.0-beta.2"
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", expected_version, language="cs"
        )
        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert result.exit_code == 0
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_update_bootloader_mode(mock_with_bootloader: None) -> None:
    """Tests the update command when in bootloader mode."""
    try:
        expected_version = "6.1.0"
        board_id = "feather_m4_express"
        result = RUNNER.invoke(
            cli, ["update", "--board-id", board_id, "--language", "cs"]
        )
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            board_id, expected_version, language="cs"
        )
        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert result.exit_code == 0
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_upgrade_successful_various_boards(mock_with_various_boards: None) -> None:
    """Tests installing when both CIRCUITPY and bootloader boards are connected."""
    with (
        create_pipe_input() as pipe,
        create_app_session(input=pipe, output=DummyOutput()),
    ):
        extra_input = "\x1b[B\r"
        pipe.send_text(extra_input)

        result = RUNNER.invoke(cli, ["update"])

    assert result.exit_code == ERR_IN_BOOTLOADER


def test_update_to_lower(mock_with_circuitpy: None) -> None:
    """Tests the update command when the current version is higher."""
    tests.helpers.set_firmware_version("100.0.0")
    tests.helpers.start_bootloader_copy_thread()

    result = RUNNER.invoke(cli, ["update", "--language", "cs"])

    mount_path = pathlib.Path(tests.helpers.get_mount())
    mount_uf2_files = list(mount_path.rglob("*.uf2"))

    assert result.exit_code == 0
    assert not mount_uf2_files


def run_limiting_test(argument: str, set_version: str, expected_version: str):
    """Test a version update limiting option."""
    try:
        tests.helpers.set_firmware_version(set_version)
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["update", argument])

        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", expected_version
        )
        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert result.exit_code == 0
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_update_limit_to_minor(mock_with_circuitpy: None) -> None:
    """Test the update command when in CIRCUITPY mode when limiting to minor updates."""
    run_limiting_test("--limit-to-minor", "7.2.0", "7.3.3")


def test_update_limit_to_patch(mock_with_circuitpy: None) -> None:
    """Test the update command when in CIRCUITPY mode when limiting to patch updates."""
    run_limiting_test("--limit-to-patch", "7.2.0", "7.2.5")


def test_update_overlimiting(mock_with_circuitpy: None) -> None:
    """Tests the update command when the current version is higher than limited options."""
    tests.helpers.set_firmware_version("1.0.0")
    tests.helpers.start_bootloader_copy_thread()

    result = RUNNER.invoke(cli, ["update", "--limit-to-patch"])

    mount_path = pathlib.Path(tests.helpers.get_mount())
    mount_uf2_files = list(mount_path.rglob("*.uf2"))

    assert result.exit_code == 1
    assert not mount_uf2_files


def test_update_bootloaders_no_board_id(mock_with_multiple_bootloaders: None) -> None:
    """Tests the update command when only bootloader boards are connected without a board ID provided."""
    result = RUNNER.invoke(cli, ["update"])
    assert result.exit_code == ERR_IN_BOOTLOADER


def test_update_timeout_failure(mock_with_circuitpy: None) -> None:
    """Tests the update command with a timeout set that times out."""
    timeout = 3
    start_time = time.time()
    result = RUNNER.invoke(cli, ["update", "--timeout", f"{timeout}"])
    assert result.exit_code != 0
    assert result.output == (
        "Board ID detected, please switch the device to bootloader mode.\n"
        "Error: Bootloader mode device not found within the timeout period\n"
    )
    assert time.time() - start_time >= timeout
