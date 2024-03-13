# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI functionality for cache command.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil

from click.testing import CliRunner

import circfirm
import circfirm.backend.cache
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


def test_cache_list() -> None:
    """Tests the cache list command."""
    # Test empty cache
    result = RUNNER.invoke(cli, ["cache", "list"])
    assert result.exit_code == 0
    assert result.output == "Versions have not been cached yet for any boards.\n"

    # Move firmware files to app directory
    tests.helpers.copy_firmwares()

    # Get full list expected response
    with open("tests/assets/responses/full_list.txt", encoding="utf-8") as respfile:
        expected_response = respfile.read()
    result = RUNNER.invoke(cli, ["cache", "list"])
    assert result.exit_code == 0
    assert result.output == expected_response

    # Test specific board that is present
    with open(
        "tests/assets/responses/specific_board.txt", encoding="utf-8"
    ) as respfile:
        expected_response = respfile.read()
    result = RUNNER.invoke(cli, ["cache", "list", "--board-id", "feather_m4_express"])
    assert result.exit_code == 0
    assert result.output == expected_response

    # Test specific board, version, and language response
    fake_board = "does_not_exist"
    with open(
        "tests/assets/responses/specific_board.txt", encoding="utf-8"
    ) as respfile:
        expected_response = respfile.read()
    result = RUNNER.invoke(cli, ["cache", "list", "--board-id", fake_board])
    assert result.exit_code == 0
    assert result.output == f"No versions for board '{fake_board}' are not cached.\n"

    # Clean Up after test
    shutil.rmtree(circfirm.UF2_ARCHIVE)
    os.mkdir(circfirm.UF2_ARCHIVE)


def test_cache_save() -> None:
    """Tests the cache save command."""
    board = "feather_m4_express"
    version = "7.3.0"
    langauge = "fr"

    # Save a specific firmware (successful)
    result = RUNNER.invoke(
        cli, ["cache", "save", board, version, "--language", langauge]
    )
    assert result.exit_code == 0
    expected_path = circfirm.backend.cache.get_uf2_filepath(
        board, version, language=langauge
    )
    assert expected_path.exists()
    shutil.rmtree(expected_path.parent.resolve())

    # Save a specific firmware (unsuccessful)
    result = RUNNER.invoke(
        cli, ["cache", "save", board, version, "--language", "nolanguage"]
    )
    assert result.exit_code == 1
    assert result.output == (
        "Caching firmware version 7.3.0 for feather_m4_express... failed\n"
        "Error: Could not download the specified UF2 file:\n"
        "https://downloads.circuitpython.org/bin/feather_m4_express/"
        "nolanguage/"
        "adafruit-circuitpython-feather_m4_express-nolanguage-7.3.0.uf2\n"
    )


def test_cache_clear() -> None:
    """Tests the cache clear command."""
    board = "feather_m4_express"
    version = "7.1.0"
    langauge = "zh_Latn_pinyin"

    # Move firmware files to app directory
    tests.helpers.copy_firmwares()

    # Remove a specific firmware from the cache
    result = RUNNER.invoke(
        cli,
        [
            "cache",
            "clear",
            "--board-id",
            board,
            "--version",
            version,
            "--language",
            langauge,
        ],
    )
    board_folder = pathlib.Path(circfirm.UF2_ARCHIVE) / board
    uf2_file = (
        board_folder
        / "adafruit-circuitpython-feather_m4_express-zh_Latn_pinyin-7.1.0.uf2"
    )
    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"
    assert not uf2_file.exists()
    assert board_folder.exists()

    # Remove a specific board firmware from the cache
    result = RUNNER.invoke(cli, ["cache", "clear", "--board-id", board])
    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"
    assert not board_folder.exists()

    # Remove entire cache
    result = RUNNER.invoke(cli, ["cache", "clear"])
    assert result.exit_code == 0
    assert result.output == "Cache cleared!\n"
    assert len(list(board_folder.parent.glob("*"))) == 0
