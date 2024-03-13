# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend device functionality.

Author(s): Alec Delaney
"""

import pytest

import circfirm.backend.device
import tests.helpers


@tests.helpers.as_circuitpy
def test_find_circuitpy() -> None:
    """Tests finding a CircuitPython device when boot_out.txt is present."""
    mount_location = tests.helpers.get_mount()
    circuitpy = circfirm.backend.device.find_circuitpy()
    assert circuitpy == mount_location


@tests.helpers.as_not_present
def test_find_circuitpy_absent() -> None:
    """Tests finding a CircuitPython device when boot_out.txt is absent."""
    circuitpy = circfirm.backend.device.find_circuitpy()
    assert circuitpy is None


@tests.helpers.as_bootloader
def test_find_bootloader() -> None:
    """Tests finding a CircuitPython device in bootloader mode when info_uf2.txt is present."""
    mount_location = tests.helpers.get_mount()
    bootloader = circfirm.backend.device.find_bootloader()
    assert bootloader == mount_location


@tests.helpers.as_not_present
def test_find_bootloader_absent() -> None:
    """Tests finding a CircuitPython device in bootloader mode when info_uf2.txt is absent."""
    bootloader = circfirm.backend.device.find_bootloader()
    assert bootloader is None
    tests.helpers.copy_uf2_info()


@tests.helpers.as_circuitpy
def test_get_board_info() -> None:
    """Tests getting the board ID and firmware version from the UF2 info file."""
    # Test successful parsing
    mount_location = tests.helpers.get_mount()
    board_id = circfirm.backend.device.get_board_info(mount_location)[0]
    assert board_id == "feather_m4_express"

    # Test unsuccessful parsing of board ID
    with open(
        tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE), mode="w", encoding="utf-8"
    ) as bootfile:
        bootfile.write("junktext")
    with pytest.raises(ValueError):
        circfirm.backend.device.get_board_info(mount_location)

    # Test unsuccessful parsing of firmware version
    with open(
        tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE), mode="w", encoding="utf-8"
    ) as bootfile:
        bootfile.write("junktext\nBoard ID:feather_m4_express")
    with pytest.raises(ValueError):
        circfirm.backend.device.get_board_info(mount_location)
