# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for install command.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
import threading
import time

from click.testing import CliRunner

import circfirm.backend
import tests.helpers
from circfirm.cli import cli


def test_install() -> None:
    """Tests the install command."""

    def wait_and_add() -> None:
        """Wait then add the boot_out.txt file."""
        time.sleep(2)
        tests.helpers.delete_mount_node(circfirm.BOOTOUT_FILE)
        tests.helpers.copy_uf2_info()

    version = "8.0.0-beta.6"
    runner = CliRunner()

    # Test successfully installing the firmware
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    tests.helpers.copy_boot_out()
    threading.Thread(target=wait_and_add).start()
    result = runner.invoke(cli, ["install", version])
    assert result.exit_code == 0
    expected_uf2_filename = circfirm.backend.get_uf2_filename(
        "feather_m4_express", version
    )
    expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
    assert os.path.exists(expected_uf2_filepath)
    os.remove(expected_uf2_filepath)

    # Test using cached version of firmware
    result = runner.invoke(cli, ["install", version, "--board", "feather_m4_express"])
    assert result.exit_code == 0
    assert "Using cached firmware file" in result.output
    os.remove(expected_uf2_filepath)

    ERR_NOT_FOUND = 1
    ERR_FOUND_CIRCUITPY = 2
    ERR_IN_BOOTLOADER = 3
    ERR_UF2_DOWNLOAD = 4

    # Test not finding the mounted drive
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    result = runner.invoke(cli, ["install", version, "--board", "feather_m4_express"])
    assert result.exit_code == ERR_NOT_FOUND

    # Test finding the mounted drive as CIRCUITPY
    tests.helpers.copy_boot_out()
    result = runner.invoke(cli, ["install", version, "--board", "feather_m4_express"])
    assert result.exit_code == ERR_FOUND_CIRCUITPY

    # Test using bad board version
    tests.helpers.delete_mount_node(circfirm.BOOTOUT_FILE)
    tests.helpers.copy_uf2_info()
    result = runner.invoke(
        cli, ["install", "doesnotexist", "--board", "feather_m4_express"]
    )
    assert result.exit_code == ERR_UF2_DOWNLOAD

    # Test using install when in bootloader mode
    result = runner.invoke(cli, ["install", version])
    assert result.exit_code == ERR_IN_BOOTLOADER

    board_folder = circfirm.backend.get_board_folder("feather_m4_express")
    shutil.rmtree(board_folder)
