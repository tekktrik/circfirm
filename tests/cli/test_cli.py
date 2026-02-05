# SPDX-FileCopyrightText: 2026 Alec Delaney
# SPDX-License-Identifier: MIT

"""Tests the core CLI functionality.

Author(s): Alec Delaney
"""

import shutil
from typing import NoReturn

import pytest

import circfirm.backend.cache
import circfirm.cli

BOARD = "feather_m0_express"
LANGUAGE = "cs"
VERSION = "6.1.0"


@pytest.mark.parametrize(
    "cached",
    (
        (True,),
        (False,),
    ),
)
def test_download_if_needed_cached(
    monkeypatch: pytest.MonkeyPatch,
    cached: bool,
) -> None:
    """Tests the install command when there is a cached firmware and has internet."""
    monkeypatch.setattr(
        circfirm.backend.cache, "is_downloaded", lambda _x, _y, _z: cached
    )
    try:
        circfirm.cli.download_if_needed(BOARD, VERSION, LANGUAGE)
    finally:
        board_folder = circfirm.backend.cache.get_board_folder(BOARD)
        if board_folder.exists():  # pragma: no cover
            shutil.rmtree(board_folder)


@pytest.mark.parametrize(
    "cached,succeeds",
    (
        (True, True),
        (False, False),
    ),
)
def test_download_if_needed_cached_no_internet(
    monkeypatch: pytest.MonkeyPatch,
    mock_no_internet: NoReturn,
    cached: bool,
    succeeds: bool,
) -> None:
    """Tests the install command when there is a cached firmware but no internet."""
    monkeypatch.setattr(
        circfirm.backend.cache, "is_downloaded", lambda _x, _y, _z: cached
    )

    try:
        if succeeds:
            circfirm.cli.download_if_needed(BOARD, VERSION, LANGUAGE)
        else:
            with pytest.raises(SystemExit):
                circfirm.cli.download_if_needed(BOARD, VERSION, LANGUAGE)
    finally:
        board_folder = circfirm.backend.cache.get_board_folder(BOARD)
        if board_folder.exists():  # pragma: no cover
            shutil.rmtree(board_folder)
