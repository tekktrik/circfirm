# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for install command.

Author(s): Alec Delaney
"""

import os
import shutil
import threading

from click.testing import CliRunner

import circfirm.backend.cache
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()

ERR_NOT_FOUND = 1
ERR_FOUND_CIRCUITPY = 2
ERR_IN_BOOTLOADER = 3
ERR_UF2_DOWNLOAD = 4

VERSION = "8.0.0-beta.6"


@tests.helpers.as_circuitpy
def test_install_successful() -> None:
    """Tests the successful use of the install command."""
    try:
        # Test successfully installing the firmware
        threading.Thread(target=tests.helpers.wait_and_set_bootloader).start()
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


@tests.helpers.as_not_present
def test_install_no_mount() -> None:
    """Tests the install command when a mounted drive is not found."""
    result = RUNNER.invoke(
        cli, ["install", VERSION, "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_NOT_FOUND


@tests.helpers.as_circuitpy
def test_install_as_circuitpy() -> None:
    """Tests the install command when a mounted CIRCUITPY drive is found."""
    result = RUNNER.invoke(
        cli, ["install", VERSION, "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_FOUND_CIRCUITPY


@tests.helpers.as_bootloader
def test_install_bad_version() -> None:
    """Tests the install command using a bad board version."""
    result = RUNNER.invoke(
        cli, ["install", "doesnotexist", "--board-id", "feather_m4_express"]
    )
    assert result.exit_code == ERR_UF2_DOWNLOAD

    # Test using install when in bootloader mode
    result = RUNNER.invoke(cli, ["install", VERSION])
    assert result.exit_code == ERR_IN_BOOTLOADER
