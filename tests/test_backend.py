# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Tests the backend functionality.

Author(s): Alec Delaney
"""

import circfirm.backend

import tests.helpers

import os
import pathlib


def test_find_circuitpy() -> None:
    """Tests finding a CircuitPython device."""
    # Test when boot_out.txt is preset
    boot_out = tests.helpers.get_mount_node(circfirm.BOOTOUT_FILE)
    tests.helpers.touch_mount_node(boot_out)

    mount_location = tests.helpers.get_mount()
    circuitpy = circfirm.backend.find_circuitpy()
    assert circuitpy == mount_location

    # Test when boot_out.txt is absent
    os.remove(boot_out)
    circuitpy = circfirm.backend.find_circuitpy()
    assert circuitpy is None

def test_find_bootloader() -> None:
    """Tests finding a CircuitPython device in bootloader mode."""
    # Test when info_uf2.txt is preset
    mount_location = tests.helpers.get_mount()
    bootloader = circfirm.backend.find_bootloader()
    assert bootloader == mount_location

    # Test when info_uf2.txt is absent
    uf2_info = tests.helpers.get_mount_node(circfirm.UF2INFO_FILE, True)
    os.remove(uf2_info)
    bootloader = circfirm.backend.find_bootloader()
    assert bootloader is None
    tests.helpers.copy_uf2_info()


def test_get_board_name() -> None:
    """Tests getting the board name from the UF2 info file."""
    mount_location = tests.helpers.get_mount()
    board_name = circfirm.backend.get_board_name(mount_location)
    assert board_name == "PyGamer"


def test_get_uf2_filepath() -> None:
    """Tests getting the UF2 filepath."""
    board_name = "feather_m4_express"
    language = "en_US"
    version = "7.0.0"

    created_path = circfirm.backend.get_uf2_filepath("Feather M4 Express", "7.0.0", "en_US", ensure=True)
    expected_path = pathlib.Path(circfirm.UF2_ARCHIVE) / board_name / f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"
    assert created_path.resolve() == expected_path.resolve()


def test_download_uf2() -> None:
    """Tests the UF2 download functionality."""
    board_name = "Feather M4 Express"
    language = "en_US"
    version = "7.0.0"

    circfirm.backend.download_uf2(board_name, version, language)
    expected_path = pathlib.Path(circfirm.UF2_ARCHIVE) / board_name / f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"

