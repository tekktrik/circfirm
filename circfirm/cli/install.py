# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the install subcommand.

Author(s): Alec Delaney
"""

import os
import shutil
import sys
import time
from typing import Optional

import click

import circfirm.backend
import circfirm.cli


@click.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option("-b", "--board", default=None, help="Assume the given board name")
def cli(version: str, language: str, board: Optional[str]) -> None:
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
        try:
            circfirm.cli.announce_and_await(
                "Downloading UF2",
                circfirm.backend.download_uf2,
                args=(board, version, language),
            )
        except ConnectionError as err:
            click.echo(" failed")  # Mark as failed
            click.echo(f"Error: {err.args[0]}")
            sys.exit(4)
    else:
        click.echo("Using cached firmware file")

    uf2file = circfirm.backend.get_uf2_filepath(board, version, language)
    uf2filename = os.path.basename(uf2file)
    uf2_path = os.path.join(bootloader, uf2filename)
    circfirm.cli.announce_and_await(
        f"Copying UF2 to {board}", shutil.copyfile, args=(uf2file, uf2_path)
    )
    click.echo("Device should reboot momentarily.")
