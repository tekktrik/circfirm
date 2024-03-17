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


def test_cache_list_empty() -> None:
    """Tests the cache list command with an empty cache."""
    result = RUNNER.invoke(cli, ["cache", "list"])
    assert result.exit_code == 0
    assert result.output == "Versions have not been cached yet for any boards.\n"


@tests.helpers.with_firmwares
def test_cache_list_all() -> None:
    """Tests the cache list command with an non-empty cache."""
    with open("tests/assets/responses/full_list.txt", encoding="utf-8") as respfile:
        expected_response = respfile.read()
    result = RUNNER.invoke(cli, ["cache", "list"])
    assert result.exit_code == 0
    assert result.output == expected_response


@tests.helpers.with_firmwares
def test_cache_list_specific_board_found() -> None:
    """Tests the cache list command with an non-empty cache for a specific board."""
    with open(
        "tests/assets/responses/specific_board.txt", encoding="utf-8"
    ) as respfile:
        expected_response = respfile.read()
    result = RUNNER.invoke(cli, ["cache", "list", "--board-id", "feather_m4_express"])
    assert result.exit_code == 0
    assert result.output == expected_response


@tests.helpers.with_firmwares
def test_cache_list_none_found() -> None:
    """Tests the cache list command with an non-empty cache and no matches."""
    fake_board = "does_not_exist"

    result = RUNNER.invoke(cli, ["cache", "list", "--board-id", fake_board])
    assert result.exit_code == 0
    assert result.output == f"No versions for board '{fake_board}' are not cached.\n"


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


@tests.helpers.with_firmwares
def test_cache_clear() -> None:
    """Tests the cache clear command."""
    board = "feather_m4_express"
    version = "7.1.0"
    language = "zh_Latn_pinyin"

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
            language,
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


@tests.helpers.with_firmwares
def test_cache_clear_regex_board_id() -> None:
    """Tests the cache clear command when using a regex flag for board ID."""
    board = "feather_m4_express"
    board_regex = "m4"

    # Remove a specific firmware from the cache
    result = RUNNER.invoke(
        cli,
        [
            "cache",
            "clear",
            "--board-id",
            board_regex,
            "--regex",
        ],
    )

    board_folder = pathlib.Path(circfirm.UF2_ARCHIVE) / board
    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"
    assert not board_folder.exists()


@tests.helpers.with_firmwares
def test_cache_clear_regex_version() -> None:
    """Tests the cache clear command when using a regex flag for version."""
    version = "7.1.0"
    version_regex = r".\.1"

    # Remove a specific firmware from the cache
    result = RUNNER.invoke(
        cli,
        [
            "cache",
            "clear",
            "--version",
            version_regex,
            "--regex",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"
    for board_folder in pathlib.Path(circfirm.UF2_ARCHIVE).glob("*"):
        assert not list(board_folder.glob(f"*{version}*"))


@tests.helpers.with_firmwares
def test_cache_clear_regex_language() -> None:
    """Tests the cache clear command when using a regex flag for language."""
    language = "zh_Latn_pinyin"
    language_regex = ".*Latn"

    # Remove a specific firmware from the cache
    result = RUNNER.invoke(
        cli,
        [
            "cache",
            "clear",
            "--language",
            language_regex,
            "--regex",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"
    for board_folder in pathlib.Path(circfirm.UF2_ARCHIVE).glob("*"):
        assert not list(board_folder.glob(f"*{language}*"))


@tests.helpers.with_firmwares
def test_cache_clear_regex_combination() -> None:
    """Tests the cache clear command when using a regex flag for language."""
    board_regex = "feather"
    version = "7.2.0"
    version_regex = r".\.2"
    language = "zh_Latn_pinyin"
    language_regex = ".*Latn"

    # Remove a specific firmware from the cache
    result = RUNNER.invoke(
        cli,
        [
            "cache",
            "clear",
            "--board-id",
            board_regex,
            "--version",
            version_regex,
            "--language",
            language_regex,
            "--regex",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "Cache cleared of specified entries!\n"

    uf2_filepath = pathlib.Path(circfirm.UF2_ARCHIVE)
    ignore_board_path = uf2_filepath / "pygamer"
    ignore_board_files = list(ignore_board_path.glob("*"))
    num_remaining_boards = 9
    assert len(ignore_board_files) == num_remaining_boards

    num_remaining_boards = 8
    for board_folder in uf2_filepath.glob("feather*"):
        deleted_filename = circfirm.backend.get_uf2_filename(
            board_folder.name, version, language
        )
        deleted_filepath = board_folder / deleted_filename
        assert not deleted_filepath.exists()
        board_files = list(board_folder.glob("*"))
        assert len(board_files) == num_remaining_boards


def test_cache_latest() -> None:
    """Test the update command when in CIRCUITPY mode."""
    board = "feather_m0_express"
    language = "cs"
    expected_version = "6.1.0"

    uf2_filepath = circfirm.backend.cache.get_uf2_filepath(
        board, expected_version, language
    )
    assert not os.path.exists(uf2_filepath)

    try:
        # Save the latest version (successful)
        result = RUNNER.invoke(cli, ["cache", "latest", board, "--language", language])
        assert result.exit_code == 0
        assert os.path.exists(uf2_filepath)

        # Save the latest version (unsuccessful)
        result = RUNNER.invoke(
            cli, ["cache", "latest", board, "--language", "doesnotexist"]
        )
        assert result.exit_code == 1

    finally:
        board_folder = circfirm.backend.cache.get_board_folder(board)
        if board_folder.exists():
            shutil.rmtree(board_folder)
