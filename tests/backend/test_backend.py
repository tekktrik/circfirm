# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend functionality.

Author(s): Alec Delaney
"""

import shutil

import pytest

import circfirm.backend.cache


def test_parse_firmware_info() -> None:
    """Tests the ability to get firmware information."""
    board_id = "feather_m4_express"
    language = "en_US"

    # Test successful parsing
    for version in ("8.0.0", "9.0.0-beta.2"):
        try:
            board_folder = circfirm.backend.cache.get_board_folder(board_id)
            circfirm.backend.cache.download_uf2(board_id, version, language)
            downloaded_filename = [file.name for file in board_folder.glob("*")][0]

            (
                parsed_version,
                parsed_language,
            ) = circfirm.backend.parse_firmware_info(downloaded_filename)
            assert parsed_version == version
            assert parsed_language == language
        finally:
            # Clean up post tests
            shutil.rmtree(board_folder)

    # Test failed parsing
    with pytest.raises(ValueError):
        circfirm.backend.parse_firmware_info("cannotparse")
