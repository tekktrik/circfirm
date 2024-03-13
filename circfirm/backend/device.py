# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Backend functionality for the working with the connected devices.

Author(s): Alec Delaney
"""

import pathlib
import re
from typing import Optional, Tuple

import psutil

import circfirm

BOARD_ID_REGEX = r"Board ID:\s*(.*)"
BOARD_VER_REGEX = (
    r"Adafruit CircuitPython (\d+\.\d+\.\d+(?:-(?:\balpha\b|\bbeta\b)\.\d+)*)"
)


def get_board_info(device_path: str) -> Tuple[str, str]:
    """Get the attached CircuitPytho board's name and version."""
    bootout_file = pathlib.Path(device_path) / circfirm.BOOTOUT_FILE
    with open(bootout_file, encoding="utf-8") as infofile:
        contents = infofile.read()
    board_match = re.search(BOARD_ID_REGEX, contents)
    if not board_match:
        raise ValueError("Could not parse the board ID from the boot out file")
    version_match = re.search(BOARD_VER_REGEX, contents)
    if not version_match:
        raise ValueError("Could not parse the firmware version from the boot out file")
    return board_match[1], version_match[1]


def _find_device(filename: str) -> Optional[str]:
    """Find a specific connected device."""
    for partition in psutil.disk_partitions():
        try:
            bootout_file = pathlib.Path(partition.mountpoint) / filename
            if bootout_file.exists():
                return partition.mountpoint
        except PermissionError:  # pragma: no cover
            pass
    return None


def find_circuitpy() -> Optional[str]:
    """Find CircuitPython device in non-bootloader mode."""
    return _find_device(circfirm.BOOTOUT_FILE)


def find_bootloader() -> Optional[str]:
    """Find CircuitPython device in bootloader mode."""
    return _find_device(circfirm.UF2INFO_FILE)
