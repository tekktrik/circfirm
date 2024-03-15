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

import circfirm.backend.github
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()


def simulate_no_connection(arg: str) -> NoReturn:
    """Simulate a network error by raising requests.ConnectionError."""
    raise requests.ConnectionError


@tests.helpers.with_token(os.environ["GH_TOKEN"])
def test_query_board_ids() -> None:
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
    assert result.exit_code == 0
    result = RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    assert result.exit_code == 0
    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code == 0
    assert result.output == pre_expected_output


@tests.helpers.with_token("badtoken")
def test_query_board_ids_bad_token() -> None:
    """Test a request with a faulty token."""
    result = RUNNER.invoke(cli, ["query", "board-ids"])
    assert result.exit_code != 0


@tests.helpers.with_token(os.environ["GH_TOKEN"], True)
def test_query_board_ids_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests failure when cannot fetch results due to no network connection."""
    monkeypatch.setattr(
        circfirm.backend.github, "get_board_id_list", simulate_no_connection
    )
    result = RUNNER.invoke(cli, ["query", "board-ids"])
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
