# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for detect command.

Author(s): Alec Delaney
"""

import pathlib

from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


def test_devices_circuitpy_found(mock_with_circuitpy: None) -> None:
    """Tests the ability of the devices circuitpy command to find a connected board."""
    result = RUNNER.invoke(cli, ["devices", "circuitpy"])
    assert result.exit_code == 0
    circuitpy = pathlib.Path(result.output.split("-")[0].strip())
    assert circuitpy.exists()
    mount = pathlib.Path(tests.helpers.get_mount())
    assert circuitpy == mount


def test_devices_circuitpy_not_found(mock_with_no_device: None) -> None:
    """Tests the detect circuitpy command without a connected board."""
    result = RUNNER.invoke(cli, ["devices", "circuitpy"])
    assert result.output == "No board connected in CIRCUITPY or equivalent mode\n"


def test_devices_bootloader_found(mock_with_bootloader: None) -> None:
    """Tests the ability of the detect bootloader command to find a connected board."""
    result = RUNNER.invoke(cli, ["devices", "bootloader"])
    assert result.exit_code == 0
    bootloader = pathlib.Path(result.output.strip())
    assert bootloader.exists()
    mount = pathlib.Path(tests.helpers.get_mount())
    assert bootloader == mount


def test_devices_bootloaders_not_found(mock_with_no_device: None) -> None:
    """Tests the detect bootloader command without a connected board."""
    result = RUNNER.invoke(cli, ["devices", "bootloader"])
    assert result.output == "No board connected in bootloader mode\n"
