# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the query subcommand.

Author(s): Alec Delaney
"""

import re

import click
import requests

import circfirm
import circfirm.backend.github
import circfirm.backend.s3
import circfirm.cli


@click.group()
def cli():
    """Query things like latest versions and board lists."""


@cli.command(name="board-ids")
@click.option(
    "-r", "--regex", default=".*", help="Regex pattern to use for board IDs (search)"
)
def query_board_ids(regex: str) -> None:
    """Query the local CircuitPython board list."""
    settings = circfirm.cli.get_settings()
    gh_token = settings["token"]["github"]
    do_output = not settings["output"]["supporting"]["silence"]
    circfirm.cli.maybe_support(
        "Boards list will now be synchronized with the git repository."
    )
    if not gh_token:  # pragma: no cover
        circfirm.cli.maybe_support(
            "Please note that this operation can only be performed 60 times per hour due to GitHub rate limiting."
        )
    try:
        if do_output:
            boards = circfirm.cli.announce_and_await(
                "Fetching boards list",
                circfirm.backend.github.get_board_id_list,
                args=(gh_token,),
            )
        else:
            boards = circfirm.backend.github.get_board_id_list(gh_token)
    except ValueError as err:
        raise click.ClickException(err.args[0])
    except requests.ConnectionError as err:
        raise click.ClickException(
            "Issue with requesting information from git repository, check network connection"
        )
    for board in boards:
        board_id = board.strip()
        result = re.search(regex, board_id)
        if result:
            click.echo(board_id)


@cli.command(name="versions")
@click.argument("board-id")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-r", "--regex", default=".*", help="Regex pattern to use for versions (match)"
)
def query_versions(board_id: str, language: str, regex: str) -> None:
    """Query the CircuitPython versions available for a board."""
    versions = circfirm.backend.s3.get_board_versions(board_id, language, regex=regex)
    for version in reversed(versions):
        click.echo(version)


@cli.command(name="latest")
@click.argument("board-id", default="raspberry_pi_pico")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-p",
    "--pre-release",
    is_flag=True,
    default=False,
    help="Consider pre-release versions",
)
def query_latest(board_id: str, language: str, pre_release: bool) -> None:
    """Query the latest CircuitPython versions available."""
    version = circfirm.backend.s3.get_latest_board_version(
        board_id, language, pre_release
    )
    if version:
        click.echo(version)
