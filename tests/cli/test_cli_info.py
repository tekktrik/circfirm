# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for info command.

Author(s): Alec Delaney
"""

from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


def test_info(mock_with_circuitpy: None) -> None:
    """Tests the current name and version commands."""
    # Test when connected in CIRCUITPY mode
    device_path = tests.helpers.get_mount()

    result = RUNNER.invoke(cli, ["info", device_path, "board-id"])
    assert result.exit_code == 0
    assert result.output == "feather_m4_express\n"

    result = RUNNER.invoke(cli, ["info", device_path, "version"])
    assert result.exit_code == 0
    assert result.output == "8.0.0-beta.6\n"


def test_info_in_bootloader(mock_with_bootloader: None) -> None:
    """Tests the current command when connected in bootloader mode."""
    device_path = tests.helpers.get_mount()
    result = RUNNER.invoke(cli, ["info", device_path, "board-id"])
    assert result.exit_code != 0
