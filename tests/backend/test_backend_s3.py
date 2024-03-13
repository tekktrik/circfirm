# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend GitHub functionality.

Author(s): Alec Delaney
"""

import circfirm.backend.s3


def test_get_board_versions() -> None:
    """Tests getting firmware versions for a given board."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_versions = [
        "6.2.0-beta.2",
        "6.2.0-beta.1",
        "6.2.0-beta.0",
    ]
    versions = circfirm.backend.s3.get_board_versions(board, language)
    assert versions == expected_versions

    # Chck that invalid versions are skipped for code coverage
    _ = circfirm.backend.s3.get_board_versions(board, regex=r".*")
