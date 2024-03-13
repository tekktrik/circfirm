# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the cache subcommand.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
import sys
from typing import Optional

import click

import circfirm
import circfirm.backend.cache
import circfirm.cli
import circfirm.startup


@click.group()
def cli():
    """Work with cached firmwares."""


@cli.command()
@click.option("-b", "--board-id", default=None, help="CircuitPython board ID")
@click.option("-v", "--version", default=None, help="CircuitPython version")
@click.option("-l", "--language", default=None, help="CircuitPython language/locale")
def clear(
    board_id: Optional[str], version: Optional[str], language: Optional[str]
) -> None:
    """Clear the cache, either entirely or for a specific board/version."""
    if board_id is None and version is None and language is None:
        shutil.rmtree(circfirm.UF2_ARCHIVE)
        circfirm.startup.ensure_app_setup()
        click.echo("Cache cleared!")
        return

    glob_pattern = "*-*" if board_id is None else f"*-{board_id}"
    language_pattern = "-*" if language is None else f"-{language}"
    glob_pattern += language_pattern
    version_pattern = "-*" if version is None else f"-{version}.uf2"
    glob_pattern += version_pattern
    matching_files = pathlib.Path(circfirm.UF2_ARCHIVE).rglob(glob_pattern)
    for matching_file in matching_files:
        matching_file.unlink()

    # Delete board folder if empty
    for board_folder in pathlib.Path(circfirm.UF2_ARCHIVE).glob("*"):
        if len(os.listdir(board_folder)) == 0:
            shutil.rmtree(board_folder)

    click.echo("Cache cleared of specified entries!")


@cli.command(name="list")
@click.option("-b", "--board-id", default=None, help="CircuitPython board ID")
def cache_list(board_id: Optional[str]) -> None:
    """List all the boards/versions cached."""
    board_list = os.listdir(circfirm.UF2_ARCHIVE)

    if not board_list:
        circfirm.cli.maybe_support("Versions have not been cached yet for any boards.")
        return

    if board_id is not None and board_id not in board_list:
        circfirm.cli.maybe_support(
            f"No versions for board '{board_id}' are not cached."
        )
        return

    specified_board = board_id if board_id is not None else None
    boards = circfirm.backend.cache.get_sorted_boards(specified_board)

    for rec_boardid, rec_boardvers in boards.items():
        click.echo(f"{rec_boardid}")
        for rec_boardver, rec_boardlangs in rec_boardvers.items():
            for rec_boardlang in rec_boardlangs:
                click.echo(f"  * {rec_boardver} ({rec_boardlang})")


@cli.command(name="save")
@click.argument("board-id")
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
def cache_save(board_id: str, version: str, language: str) -> None:
    """Install a version of CircuitPython to cache."""
    try:
        circfirm.cli.announce_and_await(
            f"Caching firmware version {version} for {board_id}",
            circfirm.backend.cache.download_uf2,
            args=(board_id, version, language),
        )
    except ConnectionError as err:
        raise click.exceptions.ClickException(err.args[0])
