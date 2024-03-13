# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the install subcommand.

Author(s): Alec Delaney
"""

from typing import Optional

import click

import circfirm.cli


@click.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-b",
    "--board-id",
    default=None,
    help="Assume the given board ID (and connect in bootloader mode)",
)
def cli(version: str, language: str, board_id: Optional[str]) -> None:
    """Install the specified version of CircuitPython."""
    circuitpy, bootloader = circfirm.cli.get_connection_status()
    bootloader, board_id = circfirm.cli.get_board_id(circuitpy, bootloader, board_id)
    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board_id, version, language)
    circfirm.cli.copy_cache_firmware(board_id, version, language, bootloader)
