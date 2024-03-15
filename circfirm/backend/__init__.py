# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Shared backend functionality.

Author(s): Alec Delaney
"""

import enum
import re
from typing import Tuple


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
_VALID_VERSIONS_CAPTURE = r"(\d+\.\d+\.\d+(?:-(?:\balpha\b|\bbeta\b)\.\d+)*)"
FIRMWARE_REGEX_PATTERN = "-".join(
    [
        r"adafruit-circuitpython",
        r"[board]",
        r"[language]",
        r"[version]\.uf2",
    ]
)
FIRMWARE_REGEX = (
    FIRMWARE_REGEX_PATTERN.replace(r"[board]", r"(.*)")
    .replace(r"[language]", f"({_ALL_LANGUAGES_REGEX})")
    .replace(r"[version]", _VALID_VERSIONS_CAPTURE)
)


def get_uf2_filename(board_id: str, version: str, language: str = "en_US") -> str:
    """Get the structured name for a specific board/version CircuitPython."""
    return f"adafruit-circuitpython-{board_id}-{language}-{version}.uf2"


def parse_firmware_info(uf2_filename: str) -> Tuple[str, str]:
    """Get firmware info."""
    regex_match = re.match(FIRMWARE_REGEX, uf2_filename)
    if regex_match is None:
        raise ValueError(
            "Firmware information could not be determined from the filename"
        )
    version = regex_match[3]
    language = regex_match[2]
    return version, language
