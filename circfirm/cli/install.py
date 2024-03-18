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
@click.option(
    "-t",
    "--timeout",
    default=-1,
    help="Set a timeout in seconds for the switch to bootloader mode",
)
def cli(version: str, language: str, board_id: Optional[str], timeout: int) -> None:
    """Install the specified version of CircuitPython."""
    circuitpy, bootloader = circfirm.cli.get_connection_status()
    try:
        bootloader, board_id = circfirm.cli.get_board_id(
            circuitpy, bootloader, board_id, timeout
        )
    except OSError as err:
        raise click.ClickException(err.args[0])
    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board_id, version, language)
    circfirm.cli.copy_cache_firmware(board_id, version, language, bootloader)
