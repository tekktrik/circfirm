# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's query command functionality.

Author(s): Alec Delaney
"""

import os
from typing import NoReturn

import pytest
import requests
from click.testing import CliRunner

import circfirm.backend
import tests.helpers
from circfirm.cli import cli


def simulate_no_connection(arg: str) -> NoReturn:
    """Simulate a network error by raising requests.ConnectionError."""
    raise requests.ConnectionError


def test_query_boards(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests the ability to query the boards using the CLI."""
    runner = CliRunner()

    # Test an unauthenticated request with supporting text
    boards = tests.helpers.get_boards_from_git()
    pre_expected_output = "".join([f"{board}\n" for board in boards])
    expected_output = "\n".join(
        [
            "Boards list will now be synchronized with the git repository.",
            "Please note that this operation can only be performed 60 times per hour due to GitHub rate limiting.",
            "Fetching boards list... done",
            pre_expected_output,
        ]
    )

    result = runner.invoke(cli, ["query", "boards"])
    assert result.exit_code == 0
    assert result.output == expected_output

    # Test an authenticated request without supporting text
    result = runner.invoke(
        cli, ["config", "edit", "token.github", os.environ["GH_TOKEN"]]
    )
    assert result.exit_code == 0
    result = runner.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["query", "boards"])
    assert result.exit_code == 0
    assert result.output == pre_expected_output

    # Test a request with a faulty token
    result = runner.invoke(cli, ["config", "edit", "token.github", "badtoken"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["query", "boards"])
    assert result.exit_code != 0

    result = runner.invoke(cli, ["config", "reset"])
    assert result.exit_code == 0

    # Tests failure when cannot fetch results due to no network connection
    monkeypatch.setattr(circfirm.backend, "get_board_list", simulate_no_connection)
    result = runner.invoke(cli, ["query", "boards"])
    assert result.exit_code != 0
    assert (
        result.output.split("\n")[-2]
        == "Error: Issue with requesting information from git repository, check network connection"
    )


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

    runner = CliRunner()
    result = runner.invoke(
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


def test_query_latest() -> None:
    """Tests the ability to query the latest version of the firmware using the CLI."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_output = "6.2.0-beta.2\n"

    # Test without pre-releases included
    runner = CliRunner()
    result = runner.invoke(
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
    result = runner.invoke(
        cli,
        ["query", "latest", board, "--language", language, "--pre-release"],
    )
    assert result.exit_code == 0
    assert result.output == expected_output
