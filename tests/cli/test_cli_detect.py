# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for detect command.

Author(s): Alec Delaney
"""

import pathlib

from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


@tests.helpers.as_circuitpy
def test_detect_circuitpy_found() -> None:
    """Tests the ability of the detect circuitpy command to find a connected board."""
    result = RUNNER.invoke(cli, ["detect", "circuitpy"])
    assert result.exit_code == 0
    circuitpy = pathlib.Path(result.output.strip())
    assert circuitpy.exists()
    mount = pathlib.Path(tests.helpers.get_mount())
    assert circuitpy == mount


@tests.helpers.as_not_present
def test_detect_circuitpy_not_found() -> None:
    """Tests the detect circuitpy command without a connected board."""
    result = RUNNER.invoke(cli, ["detect", "circuitpy"])
    assert result.output == "No board connected in CIRCUITPY or equivalent mode\n"


@tests.helpers.as_bootloader
def test_detect_bootloader_found() -> None:
    """Tests the ability of the detect bootloader command to find a connected board."""
    import time

    time.sleep(2)
    result = RUNNER.invoke(cli, ["detect", "bootloader"])
    assert result.exit_code == 0
    bootloader = pathlib.Path(result.output.strip())
    assert bootloader.exists()
    mount = pathlib.Path(tests.helpers.get_mount())
    assert bootloader == mount


@tests.helpers.as_not_present
def test_detect_bootloader_not_found() -> None:
    """Tests the detect bootloader command without a connected board."""
    result = RUNNER.invoke(cli, ["detect", "bootloader"])
    assert result.output == "No board connected in bootloader mode\n"
