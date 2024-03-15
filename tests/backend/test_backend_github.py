# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend GitHub functionality.

Author(s): Alec Delaney
"""

import os

import pytest

import circfirm.backend.github
import tests.helpers


def test_get_board_list() -> None:
    """Tests the ability of the backend to get the board list."""
    # Test successful retrieval
    token = os.environ["GH_TOKEN"]
    board_list = circfirm.backend.github.get_board_id_list(token)
    expected_board_list = tests.helpers.get_board_ids_from_git()
    assert board_list == expected_board_list

    # Test unsuccessful retrieval
    with pytest.raises(ValueError):
        circfirm.backend.github.get_board_id_list("badtoken")


def test_get_rate_limit() -> None:
    """Tests getting the rate limit for an authenticated GitHub request."""
    available, total, reset_time = circfirm.backend.github.get_rate_limit()
    total_rate_limit = 60
    assert available <= total
    assert total == total_rate_limit
    assert reset_time
