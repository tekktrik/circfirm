# SPDX-FileCopyrightText: 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

from typing import Optional
import os

import psutil
import requests

import circfirm
import circfirm.startup


def _find_device(device_name: str) -> Optional[str]:
    """Find a specific connected device."""
    for partition in psutil.disk_partitions():
        if device_name in partition.mountpoint:
            return partition.mountpoint
    return None


def find_circuitpy() -> Optional[str]:
    """Find CircuitPython device in non-bootloader mode."""
    return _find_device("CIRCUITPY")
        

def find_bootloader() -> Optional[str]:
    """Find CircuitPython device in bootloader mode."""
    for partition in psutil.disk_partitions():
        uf2info_file = os.path.join(partition.mountpoint, circfirm.UF2INFO_FILE)
        if os.path.exists(uf2info_file):
            return partition.mountpoint
    return None


def get_board_name(device_path: str) -> str:
    """Get the attached CircuitPython board's name."""
    uf2info_file = os.path.join(device_path, circfirm.UF2INFO_FILE)
    with open(uf2info_file, encoding="utf-8") as infofile:
        contents = infofile.read()
    model_line = [line.strip() for line in contents.split("\n")][1]
    return [comp.strip() for comp in model_line.split(":")][1]


def download_uf2(board: str, version: str) -> None:
    """Download a version of CircuitPython for a specific board."""
    file = circfirm.get_uf2_filename(board, version)
    board_name = board.replace(" ", "_").lower()
    uf2_file = get_uf2_path(board, version)
    url = f"https://downloads.circuitpython.org/bin/{board_name}/en_US/{file}"
    response = requests.get(url)
    with open(uf2_file, mode="wb") as uf2file:
        uf2file.write(response.content)


def is_downloaded(board: str, version: str) -> bool:
    """Check if a UF2 file is downloaded for a specific board and version."""
    uf2_file = get_uf2_path(board, version)
    return os.path.exists(uf2_file)


def get_uf2_path(board: str, version: str) -> str:
    """Get the path to a downloaded UF2 file."""
    file = circfirm.get_uf2_filename(board, version)
    board_name = board.replace(" ", "_").lower()
    uf2_folder = os.path.join(circfirm.UF2_ARCHIVE, board_name)
    circfirm.startup.ensure_dir(uf2_folder)
    return os.path.join(uf2_folder, file)
