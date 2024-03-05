# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for current command.

Author(s): Alec Delaney
"""

from click.testing import CliRunner

import circfirm
import tests.helpers
from circfirm.cli import cli


def test_current() -> None:
    """Tests the current name command."""
    runner = CliRunner()
    tests.helpers.delete_mount_node(circfirm.UF2INFO_FILE)
    tests.helpers.copy_boot_out()

    # Test when connected in CIRCUITPY mode
    result = runner.invoke(cli, ["current", "name"])
    assert result.exit_code == 0
    assert result.output == "feather_m4_express\n"

    result = runner.invoke(cli, ["current", "version"])
    assert result.exit_code == 0
    assert result.output == "8.0.0-beta.6\n"

    tests.helpers.delete_mount_node(circfirm.BOOTOUT_FILE)
    tests.helpers.copy_uf2_info()

    # Test when connected in bootloader mode
    result = runner.invoke(cli, ["current", "name"])
    assert result.exit_code != 0
