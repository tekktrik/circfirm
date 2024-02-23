# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Backend, shared functionality for the CLI.

Author(s): Alec Delaney
"""

import enum
import os
import pathlib
import re
from typing import Dict, List, Optional, Set, Tuple

import packaging.version
import psutil
import requests

import circfirm
import circfirm.startup


class Language(enum.Enum):
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


_ALL_LANGAGES = [language.value for language in Language]
_ALL_LANGUAGES_REGEX = "|".join(_ALL_LANGAGES)
FIRMWARE_REGEX = "-".join(
    [
        r"adafruit-circuitpython-(.*)",
        f"({_ALL_LANGUAGES_REGEX})",
        r"(\d+\.\d+\.\d+(?:-(?:\balpha\b|\bbeta\b)\.\d+)*)\.uf2",
    ]
)
BOARD_ID_REGEX = r"Board ID:\s*(.*)"


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


def get_board_name(device_path: str) -> str:
    """Get the attached CircuitPython board's name."""
    bootout_file = pathlib.Path(device_path) / circfirm.BOOTOUT_FILE
    with open(bootout_file, encoding="utf-8") as infofile:
        contents = infofile.read()
    board_match = re.search(BOARD_ID_REGEX, contents)
    if not board_match:
        raise ValueError("Could not parse the board name from the boot out file")
    return board_match[1]


def download_uf2(board: str, version: str, language: str = "en_US") -> None:
    """Download a version of CircuitPython for a specific board."""
    file = get_uf2_filename(board, version, language=language)
    uf2_file = get_uf2_filepath(board, version, language=language, ensure=True)
    url = f"https://downloads.circuitpython.org/bin/{board}/{language}/{file}"
    response = requests.get(url)

    SUCCESS = 200
    if response.status_code != SUCCESS:
        if not list(uf2_file.parent.glob("*")):
            uf2_file.parent.rmdir()
        raise ConnectionError(f"Could not download spectified UF2 file:\n{url}")

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
    uf2_folder = pathlib.Path(circfirm.UF2_ARCHIVE) / board
    if ensure:
        circfirm.startup.ensure_dir(uf2_folder)
    return pathlib.Path(uf2_folder) / file


def get_uf2_filename(board: str, version: str, language: str = "en_US") -> str:
    """Get the structured name for a specific board/version CircuitPython."""
    return f"adafruit-circuitpython-{board}-{language}-{version}.uf2"


def get_board_folder(board: str) -> pathlib.Path:
    """Get the board folder path."""
    return pathlib.Path(circfirm.UF2_ARCHIVE) / board


def get_firmware_info(uf2_filename: str) -> Tuple[str, str]:
    """Get firmware info."""
    regex_match = re.match(FIRMWARE_REGEX, uf2_filename)
    if regex_match is None:
        raise ValueError(
            "Firmware information could not be determined from the filename"
        )
    version = regex_match[3]
    language = regex_match[2]
    return version, language


def get_sorted_boards(board: Optional[str]) -> Dict[str, Dict[str, Set[str]]]:
    """Get a sorted collection of boards, versions, and languages."""
    boards: Dict[str, Dict[str, Set[str]]] = {}
    for board_folder in sorted(os.listdir(circfirm.UF2_ARCHIVE)):
        versions: Dict[str, List[str]] = {}
        sorted_versions: Dict[str, Set[str]] = {}
        if board is not None and board != board_folder:
            continue
        board_folder_full = pathlib.Path(circfirm.UF2_ARCHIVE) / board_folder
        for item in os.listdir(board_folder_full):
            version, language = get_firmware_info(item)
            try:
                version_set = set(versions[version])
                version_set.add(language)
                versions[version] = sorted(version_set)
            except KeyError:
                versions[version] = [language]
        for sorted_version in sorted(
            versions, reverse=True, key=packaging.version.Version
        ):
            sorted_versions[sorted_version] = versions[sorted_version]
        boards[board_folder] = sorted_versions
    return boards
