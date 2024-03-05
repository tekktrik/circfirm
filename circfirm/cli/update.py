# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the update subcommand.

Author(s): Alec Delaney
"""

from typing import Optional

import click

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
    bootloader, board = circfirm.cli.get_board_name(circuitpy, bootloader, board)
    version = circfirm.backend.get_latest_board_version(board, language, pre_release)
    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board, version, language)
    circfirm.cli.copy_cache_firmware(board, version, language, bootloader)
