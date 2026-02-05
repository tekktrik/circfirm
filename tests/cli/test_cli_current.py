# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for current command.

Author(s): Alec Delaney
"""

from click.testing import CliRunner

from circfirm.cli import cli

RUNNER = CliRunner()


def test_current(mock_with_circuitpy: None) -> None:
    """Tests the current name and version commands."""
    # Test when connected in CIRCUITPY mode
    result = RUNNER.invoke(cli, ["current", "board-id"])
    assert result.exit_code == 0
    assert result.output == "feather_m4_express\n"

    result = RUNNER.invoke(cli, ["current", "version"])
    assert result.exit_code == 0
    assert result.output == "8.0.0-beta.6\n"


def test_current_in_bootloader(mock_with_bootloader: None) -> None:
    """Tests the current command whenn connected in bootloader mode."""
    result = RUNNER.invoke(cli, ["current", "board-id"])
    assert result.exit_code != 0
