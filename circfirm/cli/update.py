# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the update subcommand.

Author(s): Alec Delaney
"""

from typing import Optional

import click
import packaging.version

import circfirm.backend
import circfirm.cli.install


@click.option(
    "-b",
    "--board",
    default=None,
    help="Assume the given board name (and connect in bootloader mode)",
)
@click.option("-l", "--language", default="en_US", help="CircuitPython langauge/locale")
@click.option(
    "-p",
    "--pre-release",
    is_flag=True,
    default=False,
    help="Whether pre-release versions should be considered",
)
def cli(board: Optional[str], language: str, pre_release: bool) -> None:
    """Update a connected board to the latest CircuitPython version."""
    circuitpy, bootloader = circfirm.cli.get_connection_status()
    if not board and circuitpy:
        _, current_version = circfirm.backend.get_board_info(circuitpy)
    bootloader, board = circfirm.cli.get_board_name(circuitpy, bootloader, board)

    new_version = circfirm.backend.get_latest_board_version(
        board, language, pre_release
    )
    if packaging.version.Version(current_version) >= packaging.version.Version(
        new_version
    ):
        click.echo(
            f"Current version ({current_version}) is at or higher than proposed new update ({new_version})"
        )
        return

    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board, new_version, language)
    circfirm.cli.copy_cache_firmware(board, new_version, language, bootloader)
