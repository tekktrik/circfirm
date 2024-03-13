# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Shared backend functionality.

Author(s): Alec Delaney
"""

import enum


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
