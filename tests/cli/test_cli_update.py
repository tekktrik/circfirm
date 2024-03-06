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

RUNNER = CliRunner()

ORIGINAL_VERSION = "6.0.0"


@tests.helpers.as_circuitpy
def test_update() -> None:
    """Test the update command when in CIRCUITPY mode."""
    try:
        tests.helpers.set_firmware_version(ORIGINAL_VERSION)

        threading.Thread(target=tests.helpers.wait_and_set_bootloader).start()
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
        board_folder = circfirm.backend.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)


@tests.helpers.as_circuitpy
def test_update_pre_release() -> None:
    """Tests the update command when in CIRCUITPY mode with the pre-release flag."""
    try:
        tests.helpers.set_firmware_version(ORIGINAL_VERSION)

        threading.Thread(target=tests.helpers.wait_and_set_bootloader).start()
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
        board_folder = circfirm.backend.get_board_folder("feather_m4_express")
        if board_folder.exists():
            shutil.rmtree(board_folder)
