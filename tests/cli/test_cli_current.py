# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for current command.

Author(s): Alec Delaney
"""

from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


@tests.helpers.as_circuitpy
def test_current() -> None:
    """Tests the current name and version commands."""
    # Test when connected in CIRCUITPY mode
    result = RUNNER.invoke(cli, ["current", "board-id"])
    assert result.exit_code == 0
    assert result.output == "feather_m4_express\n"

    result = RUNNER.invoke(cli, ["current", "version"])
    assert result.exit_code == 0
    assert result.output == "8.0.0-beta.6\n"


@tests.helpers.as_bootloader
def test_current_in_bootloader() -> None:
    """Tests the current command whenn connected in bootloader mode."""
    result = RUNNER.invoke(cli, ["current", "board-id"])
    assert result.exit_code != 0
