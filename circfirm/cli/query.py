# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the query subcommand.

Author(s): Alec Delaney
"""

import re

import click
import packaging.version
import requests

import circfirm
import circfirm.backend
import circfirm.cli


@click.group()
def cli():
    """Query things like latest versions and board lists."""


@cli.command(name="boards")
@click.option(
    "-r", "--regex", default=".*", help="Regex pattern to use for board names"
)
def query_boards(regex: str) -> None:
    """Query the local CircuitPython board list."""
    settings = circfirm.cli.get_settings()
    gh_token = settings["token"]["github"]
    do_output = not settings["output"]["supporting"]["silence"]
    circfirm.cli.maybe_support(
        "Boards list will now be synchronized with the git repository."
    )
    if not gh_token:
        circfirm.cli.maybe_support(
            "Please note that this operation can only be performed 60 times per hour due to GitHub rate limiting."
        )
    try:
        if do_output:
            boards = circfirm.cli.announce_and_await(
                "Fetching boards list",
                circfirm.backend.get_board_list,
                args=(gh_token,),
            )
        else:
            boards = circfirm.backend.get_board_list(gh_token)
    except ValueError as err:
        raise click.ClickException(err.args[0])
    except requests.ConnectionError as err:
        raise click.ClickException(
            "Issue with requesting information from git repository, check network connection"
        )
    for board in boards:
        board_name = board.strip()
        result = re.match(regex, board_name)
        if result:
            click.echo(board_name)


@cli.command(name="versions")
@click.argument("board")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option("-r", "--regex", default=".*", help="Regex pattern to use for versions")
def query_versions(board: str, language: str, regex: str) -> None:
    """Query the CircuitPython versions available for a board."""
    versions = circfirm.backend.get_board_versions(board, language, regex=regex)
    for version in reversed(versions):
        click.echo(version)


@cli.command(name="latest")
@click.argument("board", default="raspberry_pi_pico")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-p",
    "--pre-release",
    is_flag=True,
    default=False,
    help="Consider pre-release versions",
)
def query_latest(board: str, language: str, pre_release: bool) -> None:
    """Query the latest CircuitPython versions available."""
    versions = circfirm.backend.get_board_versions(board, language)
    if not pre_release:
        versions = [
            version
            for version in versions
            if not packaging.version.Version(version).is_prerelease
        ]
    if versions:
        click.echo(versions[0])
