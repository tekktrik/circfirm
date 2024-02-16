# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Backend, shared functionality for the CLI.

Author(s): Alec Delaney
"""

import enum
import pathlib
import sys
from typing import Optional, Tuple

import click
import psutil
import requests

import circfirm
import circfirm.startup


class Languages(enum.Enum):
    """Avaiable languages for boards."""

    BAHASA_INDONESIAN = "ID"
    CZECH = "cs"
    GERMAN = "de_DE"
    UK_ENGLISH = "en_GB"
    US_ENGLISH = "en_US"
    PIRATE_ENGLISH = "en_x_pirate"
    SPANISH = "es"
    FILIPINO = "fil"
    FRENCH = "fr"
    HINDI = "hi"
    ITALIAN = "it_IT"
    JAPANESE = "ja"
    KOREAN = "ko"
    DUTCH = "nl"
    POLISH = "pl"
    BRAZILIAN_PORTUGESE = "pt_BR"
    RUSSIAN = "ru"
    SWEDISH = "sv"
    TURKISH = "tr"
    MANDARIN_LATIN_PINYIN = "zh_Latn_pinyin"


def _find_device(filename: str) -> Optional[str]:
    """Find a specific connected device."""
    for partition in psutil.disk_partitions():
        try:
            bootout_file = pathlib.Path(partition.mountpoint) / filename
            if bootout_file.exists():
                return partition.mountpoint
        except PermissionError:
            pass
    return None


def find_circuitpy() -> Optional[str]:
    """Find CircuitPython device in non-bootloader mode."""
    return _find_device(circfirm.BOOTOUT_FILE)


def find_bootloader() -> Optional[str]:
    """Find CircuitPython device in bootloader mode."""
    return _find_device(circfirm.UF2INFO_FILE)


def get_board_name(device_path: str) -> str:
    """Get the attached CircuitPython board's name."""
    uf2info_file = pathlib.Path(device_path) / circfirm.UF2INFO_FILE
    with open(uf2info_file, encoding="utf-8") as infofile:
        contents = infofile.read()
    model_line = [line.strip() for line in contents.split("\n")][1]
    return [comp.strip() for comp in model_line.split(":")][1]


def download_uf2(board: str, version: str, language: str = "en_US") -> None:
    """Download a version of CircuitPython for a specific board."""
    file = get_uf2_filename(board, version)
    board_name = board.replace(" ", "_").lower()
    uf2_file = get_uf2_filepath(board, version, ensure=True)
    url = f"https://downloads.circuitpython.org/bin/{board_name}/{language}/{file}"
    response = requests.get(url)

    if response.status_code != 200:
        uf2_file.parent.rmdir()
        click.echo("Error downloading the requests UF2 file.")
        click.echo("Please check the name and version of the board.")
        sys.exit(1)

    with open(uf2_file, mode="wb") as uf2file:
        uf2file.write(response.content)


def is_downloaded(board: str, version: str, language: str = "en_US") -> bool:
    """Check if a UF2 file is downloaded for a specific board and version."""
    uf2_file = get_uf2_filepath(board, version, language)
    return uf2_file.exists()


def get_uf2_filepath(
    board: str, version: str, language: str = "en_US", *, ensure: bool = False
) -> pathlib.Path:
    """Get the path to a downloaded UF2 file."""
    file = get_uf2_filename(board, version, language)
    board_name = board.replace(" ", "_").lower()
    uf2_folder = pathlib.Path(circfirm.UF2_ARCHIVE) / board_name
    if ensure:
        circfirm.startup.ensure_dir(uf2_folder)
    return pathlib.Path(uf2_folder) / file


def get_uf2_filename(board: str, version: str, language: str = "en_US") -> str:
    """Get the structured name for a specific board/version CircuitPython."""
    board_name = board.replace(" ", "_").lower()
    return f"adafruit-circuitpython-{board_name}-{language}-{version}.uf2"


def get_board_folder(board: str) -> pathlib.Path:
    """Get the board folder path."""
    board_name = board.replace(" ", "_").lower()
    return pathlib.Path(circfirm.UF2_ARCHIVE) / board_name


def get_firmware_info(uf2_filename: str) -> Tuple[str, str]:
    """Get firmware info."""
    filename_parts = uf2_filename.split("-")
    language = filename_parts[-2]
    version = filename_parts[-1][:-4]
    return version, language
