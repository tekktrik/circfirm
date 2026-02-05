# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's query command functionality.

Author(s): Alec Delaney
"""

import os
from typing import NoReturn

import pytest
from click.testing import CliRunner

import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


def test_query_board_ids(token: None) -> None:
    """Tests the ability to query the boards using the CLI."""
    # Test an authenticated request with supporting text
    board_ids = tests.helpers.get_board_ids_from_git()
    pre_expected_output = "".join([f"{board}\n" for board in board_ids])
    expected_output = "\n".join(
        [
            "Boards list will now be synchronized with the git repository.",
            "Fetching boards list... done",
            pre_expected_output,
        ]
    )

    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code == 0
    assert result.output == expected_output

    # Test an authenticated request without supporting text
    preexisting = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    preexisting = preexisting.output.strip()
    assert preexisting in ("true", "false")

    # Suppress supporting text
    result = RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    assert result.exit_code == 0

    # Test command
    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code == 0
    assert result.output == pre_expected_output

    # Reset the supporting text setting
    result = RUNNER.invoke(
        cli, ["config", "edit", "output.supporting.silence", preexisting]
    )
    assert result.exit_code == 0

    # Check results of reset
    final = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    final = final.output.strip()
    assert final == preexisting


@pytest.mark.parametrize("token", ["badtoken"], indirect=True)
def test_query_board_ids_bad_token(token: None) -> None:
    """Test a request with a faulty token."""
    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code != 0


def test_query_board_ids_no_internet(
    token: None, mock_requests_no_internet: NoReturn
) -> None:
    """Tests failure when cannot fetch results due to no network connection."""
    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code != 0


def test_query_board_ids_bad_regex(token: None) -> None:
    """Tests failure when a bad regex pattern is provided."""
    result = RUNNER.invoke(cli, ["query", "board-ids", "--regex", "*badregex"])
    assert result.exit_code != 0


def test_query_versions() -> None:
    """Tests the ability to query firmware versions using the CLI."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_versions = [
        "6.2.0-beta.0",
        "6.2.0-beta.1",
        "6.2.0-beta.2",
    ]
    expected_output = "".join([f"{version}\n" for version in expected_versions])

    result = RUNNER.invoke(
        cli,
        [
            "query",
            "versions",
            board,
            "--language",
            language,
        ],
    )
    assert result.exit_code == 0
    assert result.output == expected_output

    # Test the regex flag
    result = RUNNER.invoke(
        cli,
        [
            "query",
            "versions",
            board,
            "--language",
            language,
            "--regex",
            "^.*beta.1$",
        ],
    )
    assert result.exit_code == 0
    assert result.output == "6.2.0-beta.1\n"


def test_query_versions_no_internet(mock_s3_no_internet: NoReturn) -> None:
    """Tests the ability to query firmware versions using the CLI."""
    board = "adafruit_feather_rp2040"
    language = "cs"

    result = RUNNER.invoke(
        cli,
        [
            "query",
            "versions",
            board,
            "--language",
            language,
        ],
    )

    assert result.exit_code != 0


def test_query_versions_bad_regex(token: None) -> None:
    """Tests failure when a bad regex pattern is provided."""
    result = RUNNER.invoke(
        cli, ["query", "versions", "adafruit_feather_rp2040", "--regex", "*badregex"]
    )
    assert result.exit_code != 0


def test_query_latest() -> None:
    """Tests the ability to query the latest version of the firmware using the CLI."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_output = "6.2.0-beta.2\n"

    # Test without pre-releases included
    result = RUNNER.invoke(
        cli,
        [
            "query",
            "latest",
            board,
            "--language",
            language,
        ],
    )
    assert result.exit_code == 0
    assert result.output == ""

    # Test with pre-releases included
    result = RUNNER.invoke(
        cli,
        ["query", "latest", board, "--language", language, "--pre-release"],
    )
    assert result.exit_code == 0
    assert result.output == expected_output


def test_query_latest_no_internet(mock_s3_no_internet: NoReturn) -> None:
    """Tests the ability to query the latest version of the firmware using the CLI."""
    board = "adafruit_feather_rp2040"
    language = "cs"

    # Test without pre-releases included
    result = RUNNER.invoke(
        cli,
        [
            "query",
            "latest",
            board,
            "--language",
            language,
        ],
    )
    assert result.exit_code != 0
