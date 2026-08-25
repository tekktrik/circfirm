# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for install command.

Author(s): Alec Delaney
"""

import os
import shutil
import time

import pytest
from click.testing import CliRunner
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

import circfirm.backend.cache
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()

ERR_NOT_FOUND = 1
ERR_FOUND_CIRCUITPY = 2
ERR_IN_BOOTLOADER = 3
ERR_UF2_DOWNLOAD = 4

VERSION = "8.0.0-beta.6"


def test_install_successful(mock_with_circuitpy: None) -> None:
    """Tests the successful use of the install command."""
    try:
        # Test successfully installing the firmware
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["install", VERSION])

        assert result.exit_code == 0
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", VERSION
        )

        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

        # Test using cached version of firmware
        result = RUNNER.invoke(
            cli, ["install", VERSION, "--board-id", "feather_m4_express"]
        )
        assert result.exit_code == 0
        assert "Using cached firmware file" in result.output
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


@pytest.mark.parametrize("mount_index", (0, 1))
def test_install_successful_multiple_boards(
    mock_with_multiple_circuitpys: None, mount_index: int
) -> None:
    """Tests the successful use of the install command."""
    try:
        with create_pipe_input() as pipe:
            with create_app_session(input=pipe, output=DummyOutput()):
                extra_input = ""
                for i in range(mount_index):
                    extra_input += "\x1b[B"
                extra_input += "\r"

                pipe.send_text(extra_input)

                # Test successfully installing the firmware
                tests.helpers.start_bootloader_copy_thread(mount_index)

                result = RUNNER.invoke(cli, ["install", VERSION])

        assert result.exit_code == 0
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", VERSION
        )

        expected_uf2_filepath = tests.helpers.get_mount_node(
            expected_uf2_filename, mount_index
        )
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_install_multiple_bootloaders(mock_with_circuitpy: None) -> None:
    """Tests the successful use of the install command."""
    try:
        # Test installing the firmware where mutliple bootloaders are detected
        tests.helpers.start_multiple_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["install", VERSION])

        assert result.exit_code == 1
        assert (
            result.stderr
            == "Error: More than one bootloader was added, cannot confirm the intended target\n"
        )

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():  # pragma: no cover
            shutil.rmtree(board_folder)


def test_install_no_mount(mock_with_no_device: None) -> None:
    """Tests the install command when a mounted drive is not found."""
    result = RUNNER.invoke(
        cli, ["install", VERSION, "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_NOT_FOUND


def test_install_as_circuitpy(mock_with_circuitpy: None) -> None:
    """Tests the install command when a mounted CIRCUITPY drive is found."""
    result = RUNNER.invoke(
        cli, ["install", VERSION, "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_FOUND_CIRCUITPY


def test_install_bad_version(mock_with_bootloader: None) -> None:
    """Tests the install command using a bad board version."""
    result = RUNNER.invoke(
        cli, ["install", "doesnotexist", "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_UF2_DOWNLOAD

    # Test using install when in bootloader mode
    result = RUNNER.invoke(cli, ["install", VERSION])
    assert result.exit_code == ERR_IN_BOOTLOADER


def test_install_with_timeout(mock_with_circuitpy: None) -> None:
    """Tests the install command using the timeout option."""
    try:
        tests.helpers.start_bootloader_copy_thread()

        result = RUNNER.invoke(cli, ["install", VERSION, "--timeout", "60"])

        assert result.exit_code == 0
        expected_uf2_filename = circfirm.backend.get_uf2_filename(
            "feather_m4_express", VERSION
        )

        expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
        assert os.path.exists(expected_uf2_filepath)
        os.remove(expected_uf2_filepath)

    finally:
        board_folder = circfirm.backend.cache.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


def test_install_with_timeout_failure(mock_with_circuitpy: None) -> None:
    """Tests the install command using the timeout option that causes a failure."""
    timeout = 3
    start_time = time.time()
    result = RUNNER.invoke(cli, ["install", VERSION, "--timeout", f"{timeout}"])
    assert result.exit_code != 0
    assert result.output == (
        "Board ID detected, please switch the device to bootloader mode.\n"
        "Error: Bootloader mode device not found within the timeout period\n"
    )
    assert time.time() - start_time >= timeout
