# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Backend functionality for the working with the cache.

Author(s): Alec Delaney
"""

import os
import pathlib
import re
from typing import Dict, List, Optional, Set, Tuple

import packaging.version
import requests

import circfirm.backend
import circfirm.startup


def get_uf2_filename(board_id: str, version: str, language: str = "en_US") -> str:
    """Get the structured name for a specific board/version CircuitPython."""
    return f"adafruit-circuitpython-{board_id}-{language}-{version}.uf2"


def get_uf2_filepath(
    board_id: str, version: str, language: str = "en_US"
) -> pathlib.Path:
    """Get the path to a downloaded UF2 file."""
    file = get_uf2_filename(board_id, version, language)
    uf2_folder = get_board_folder(board_id)
    return uf2_folder / file


def get_board_folder(board_id: str) -> pathlib.Path:
    """Get the board folder path."""
    return pathlib.Path(circfirm.UF2_ARCHIVE) / board_id


def is_downloaded(board_id: str, version: str, language: str = "en_US") -> bool:
    """Check if a UF2 file is downloaded for a specific board and version."""
    uf2_file = get_uf2_filepath(board_id, version, language)
    return uf2_file.exists()


def download_uf2(board_id: str, version: str, language: str = "en_US") -> None:
    """Download a version of CircuitPython for a specific board."""
    file = get_uf2_filename(board_id, version, language=language)
    uf2_file = get_uf2_filepath(board_id, version, language=language)
    url = f"https://downloads.circuitpython.org/bin/{board_id}/{language}/{file}"
    response = requests.get(url)

    SUCCESS = 200
    if response.status_code != SUCCESS:
        raise ConnectionError(f"Could not download the specified UF2 file:\n{url}")

    uf2_file.parent.mkdir(parents=True, exist_ok=True)
    with open(uf2_file, mode="wb") as uf2file:
        uf2file.write(response.content)


def get_sorted_boards(board_id: Optional[str]) -> Dict[str, Dict[str, Set[str]]]:
    """Get a sorted collection of boards, versions, and languages."""
    boards: Dict[str, Dict[str, Set[str]]] = {}
    for board_folder in sorted(os.listdir(circfirm.UF2_ARCHIVE)):
        versions: Dict[str, List[str]] = {}
        sorted_versions: Dict[str, Set[str]] = {}
        if board_id is not None and board_id != board_folder:
            continue
        board_folder_full = get_board_folder(board_folder)
        for item in os.listdir(board_folder_full):
            version, language = parse_firmware_info(item)
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


def parse_firmware_info(uf2_filename: str) -> Tuple[str, str]:
    """Get firmware info."""
    regex_match = re.match(circfirm.backend.FIRMWARE_REGEX, uf2_filename)
    if regex_match is None:
        raise ValueError(
            "Firmware information could not be determined from the filename"
        )
    version = regex_match[3]
    language = regex_match[2]
    return version, language
