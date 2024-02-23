# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Main CLI functionality for the tool.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
import sys
import time
from typing import Any, Callable, Dict, Iterable, Optional

import click

import circfirm
import circfirm.backend
import circfirm.startup


@click.group()
@click.version_option(package_name="circfirm")
def cli() -> None:
    """Install CircuitPython firmware from the command line."""
    circfirm.startup.ensure_app_setup()


def announce_and_await(
    msg: str,
    func: Callable,
    args: Iterable = (),
    kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Announce an action to be performed, do it, then announce its completion."""
    if kwargs is None:
        kwargs = {}
    fmt_msg = f"{msg}..."
    click.echo(fmt_msg, nl=False)
    resp = func(*args, **kwargs)
    click.echo(" done")
    return resp


@cli.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option("-b", "--board", default=None, help="Assume the given board name")
def install(version: str, language: str, board: Optional[str]) -> None:
    """Install the specified version of CircuitPython."""
    circuitpy = circfirm.backend.find_circuitpy()
    bootloader = circfirm.backend.find_bootloader()
    if not circuitpy and not bootloader:
        click.echo("CircuitPython device not found!")
        click.echo("Check that the device is connected and mounted.")
        sys.exit(1)

    if not board:
        if not circuitpy and bootloader:
            click.echo("CircuitPython device found, but it is in bootloader mode!")
            click.echo(
                "Please put the device out of bootloader mode, or use the --board option."
            )
            sys.exit(3)
        board = circfirm.backend.get_board_name(circuitpy)

        click.echo("Board name detected, please switch the device to bootloader mode.")
        while not (bootloader := circfirm.backend.find_bootloader()):
            time.sleep(1)

    if not bootloader:
        if circfirm.backend.find_circuitpy():
            click.echo("CircuitPython device found, but is not in bootloader mode!")
            click.echo("Please put the device in bootloader mode.")
            sys.exit(2)

    if not circfirm.backend.is_downloaded(board, version, language):
        announce_and_await(
            "Downloading UF2",
            circfirm.backend.download_uf2,
            args=(board, version, language),
        )
    else:
        click.echo(f"Using cached firmware file")

    uf2file = circfirm.backend.get_uf2_filepath(board, version, language)
    uf2filename = os.path.basename(uf2file)
    uf2_path = os.path.join(bootloader, uf2filename)
    announce_and_await(
        f"Copying UF2 to {board}", shutil.copyfile, args=(uf2file, uf2_path)
    )
    click.echo("Device should reboot momentarily.")


@cli.group()
def cache():
    """Work with cached information."""


@cache.command()
@click.option("-b", "--board", default=None, help="CircuitPythonoard name")
@click.option("-v", "--version", default=None, help="CircuitPython version")
@click.option("-l", "--language", default=None, help="CircuitPython language/locale")
def clear(
    board: Optional[str], version: Optional[str], language: Optional[str]
) -> None:
    """Clear the cache, either entirely or for a specific board/version."""
    if board is None and version is None and language is None:
        shutil.rmtree(circfirm.UF2_ARCHIVE)
        circfirm.startup.ensure_app_setup()
        click.echo("Cache cleared!")
        return

    glob_pattern = "*-*" if board is None else f"*-{board}"
    language_pattern = "-*" if language is None else f"-{language}"
    glob_pattern += language_pattern
    version_pattern = "-*" if version is None else f"-{version}*"
    glob_pattern += version_pattern
    matching_files = pathlib.Path(circfirm.UF2_ARCHIVE).rglob(glob_pattern)
    for matching_file in matching_files:
        matching_file.unlink()

    # Delete board folder if empty
    for board_folder in pathlib.Path(circfirm.UF2_ARCHIVE).glob("*"):
        if len(os.listdir(board_folder)) == 0:
            shutil.rmtree(board_folder)

    click.echo("Cache cleared of specified entries!")


@cache.command(name="list")
@click.option("-b", "--board", default=None, help="CircuitPython board name")
def cache_list(board: Optional[str]) -> None:
    """List all the boards/versions cached."""
    board_list = os.listdir(circfirm.UF2_ARCHIVE)

    if not board_list:
        click.echo("Versions have not been cached yet for any boards.")
        sys.exit(0)

    if board is not None and board not in board_list:
        click.echo(f"No versions for board '{board}' are not cached.")
        sys.exit(0)

    specified_board = board if board is not None else None
    boards = circfirm.backend.get_sorted_boards(specified_board)

    for rec_boardname, rec_boardvers in boards.items():
        click.echo(f"{rec_boardname}")
        for rec_boardver, rec_boardlangs in rec_boardvers.items():
            for rec_boardlang in rec_boardlangs:
                click.echo(f"  * {rec_boardver} ({rec_boardlang})")


@cache.command(name="save")
@click.argument("board")
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
def cache_save(board: str, version: str, language: str) -> None:
    """Install a version of CircuitPython to cache."""
    try:
        announce_and_await(
            f"Caching firmware version {version} for {board}",
            circfirm.backend.download_uf2,
            args=(board, version, language),
        )
    except ConnectionError as err:
        raise click.exceptions.ClickException(err.args[0])
