# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the backend device functionality.

Author(s): Alec Delaney
"""

import pytest

import circfirm.backend.device
import tests.helpers


def test_find_circuitpys(mock_with_multiple_circuitpys: None) -> None:
    """Tests finding a CircuitPython device when boot_out.txt is present on multiple devices."""
    mount_location_0 = tests.helpers.get_mount(0)
    mount_location_1 = tests.helpers.get_mount(1)
    circuitpys = circfirm.backend.device.find_circuitpys()
    detected_mounts = set(circuitpys)
    actual_mounts = {mount_location_0, mount_location_1}
    assert detected_mounts == actual_mounts


def test_find_bootloaders(mock_with_multiple_bootloaders: None) -> None:
    """Tests finding a CircuitPython device in bootloader mode when info_uf2.txt is present on multiple devices."""
    mount_location_0 = tests.helpers.get_mount(0)
    mount_location_1 = tests.helpers.get_mount(1)
    bootloaders = circfirm.backend.device.find_bootloaders()
    detected_mounts = set(bootloaders)
    actual_mounts = {mount_location_0, mount_location_1}
    assert detected_mounts == actual_mounts


def test_get_board_info_from_circuitpy(mock_with_circuitpy: None) -> None:
    """Tests getting the board ID and firmware version from the UF2 info file."""
    # Test successful parsing
    mount_location = tests.helpers.get_mount()
    board_id = circfirm.backend.device.get_board_info_from_circuitpy(mount_location)[0]
    assert board_id == "feather_m4_express"

    # Test unsuccessful parsing of board ID
    with open(
        tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE), mode="w", encoding="utf-8"
    ) as bootfile:
        bootfile.write("junktext")
    with pytest.raises(ValueError):
        circfirm.backend.device.get_board_info_from_circuitpy(mount_location)

    # Test unsuccessful parsing of firmware version
    with open(
        tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE), mode="w", encoding="utf-8"
    ) as bootfile:
        bootfile.write("junktext\nBoard ID:feather_m4_express")
    with pytest.raises(ValueError):
        circfirm.backend.device.get_board_info_from_circuitpy(mount_location)
