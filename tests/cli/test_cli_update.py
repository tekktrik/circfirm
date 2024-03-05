# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for update command.

Author(s): Alec Delaney
"""

import os
import shutil
import threading

from click.testing import CliRunner

import circfirm
import circfirm.backend
import tests.helpers
from circfirm.cli import cli


def test_update() -> None:
    """Tests the update command."""
    runner = CliRunner()
    original_version = "6.0.0"

    # Test the update command when in CIRCUITPY mode
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    tests.helpers.copy_boot_out()
    tests.helpers.set_firmware_version(original_version)

    threading.Thread(target=tests.helpers.wait_and_set_bootloader).start()
    result = runner.invoke(cli, ["update", "--language", "cs"])
    expected_version = "6.1.0"
    expected_uf2_filename = circfirm.backend.get_uf2_filename(
        "feather_m4_express", expected_version, language="cs"
    )
    expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
    assert result.exit_code == 0
    assert os.path.exists(expected_uf2_filepath)
    os.remove(expected_uf2_filepath)

    # Test the update command when in CIRCUITPY mode with the pre-release flag
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    tests.helpers.copy_boot_out()
    tests.helpers.set_firmware_version(original_version)

    threading.Thread(target=tests.helpers.wait_and_set_bootloader).start()
    result = runner.invoke(cli, ["update", "--language", "cs", "--pre-release"])
    expected_version = "6.2.0-beta.2"
    expected_uf2_filename = circfirm.backend.get_uf2_filename(
        "feather_m4_express", expected_version, language="cs"
    )
    expected_uf2_filepath = tests.helpers.get_mount_node(expected_uf2_filename)
    assert result.exit_code == 0
    assert os.path.exists(expected_uf2_filepath)
    os.remove(expected_uf2_filepath)

    # Reset state after tests
    board_folder = circfirm.backend.get_board_folder("feather_m4_express")
    shutil.rmtree(board_folder)
