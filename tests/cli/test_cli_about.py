# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for about command.

Author(s): Alec Delaney
"""

from click.testing import CliRunner

from circfirm.cli import cli


def test_about() -> None:
    """Tests the about command."""
    runner = CliRunner()

    result = runner.invoke(cli, ["about"])
    assert result.exit_code == 0
    assert result.output == "Written by Alec Delaney, licensed under MIT License.\n"
