# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the install subcommand.

Author(s): Alec Delaney
"""

from typing import Optional

import click

import circfirm.backend
import circfirm.cli


@click.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-b",
    "--board",
    default=None,
    help="Assume the given board name (and connect in bootloader mode)",
)
def cli(version: str, language: str, board: Optional[str]) -> None:
    """Install the specified version of CircuitPython."""
    circuitpy, bootloader = circfirm.cli.get_connection_status()
    bootloader, board = circfirm.cli.get_board_name(circuitpy, bootloader, board)
    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board, version, language)
    circfirm.cli.copy_cache_firmware(board, version, language, bootloader)
