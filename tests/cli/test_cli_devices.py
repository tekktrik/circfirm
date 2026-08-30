# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for detect command.

Author(s): Alec Delaney
"""

import pathlib

from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli
from tests.helpers import N_DEVICES

RUNNER = CliRunner()


def test_devices(mock_with_various_boards: None) -> None:
    """Tests the default devices subcommand."""
    result = RUNNER.invoke(cli, ["devices"])
    assert result.exit_code == 0

    device_paths = [tests.helpers.get_mount(i) for i in range(N_DEVICES)]
    expected_output = ""
    for i, dp in enumerate(sorted(device_paths)):
        if not i:
            formatted = f"{dp} - feather_m4_express (8.0.0-beta.6) [CIRCUITPY]\n"
        else:
            formatted = f"{dp} [bootloader]\n"
        expected_output += formatted
    assert result.output == expected_output


def test_devices_none_connected(mock_with_no_device: None) -> None:
    """Tests the default devices subcommand when no devices are connected."""
    result = RUNNER.invoke(cli, ["devices"])
    assert result.exit_code == 0
    assert (
        result.output == "No boards connected in either CIRCUITPY or bootloader modes\n"
    )


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
