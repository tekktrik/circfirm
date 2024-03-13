# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the update subcommand.

Author(s): Alec Delaney
"""

from typing import Optional

import click
import packaging.version

import circfirm.backend.device
import circfirm.backend.s3
import circfirm.cli.install


@click.command()
@click.option(
    "-b",
    "--board-id",
    default=None,
    help="Assume the given board ID (and connect in bootloader mode)",
)
@click.option("-l", "--language", default="en_US", help="CircuitPython langauge/locale")
@click.option(
    "-p",
    "--pre-release",
    is_flag=True,
    default=False,
    help="Whether pre-release versions should be considered",
)
def cli(board_id: Optional[str], language: str, pre_release: bool) -> None:
    """Update a connected board to the latest CircuitPython version."""
    circuitpy, bootloader = circfirm.cli.get_connection_status()
    if circuitpy:
        _, current_version = circfirm.backend.device.get_board_info(circuitpy)
    else:
        click.echo(
            "Bootloader mode detected - cannot check the currently installed version"
        )
        click.echo(
            "The latest version will be installed regardless of the currently installed version."
        )
        current_version = "0.0.0"
    bootloader, board_id = circfirm.cli.get_board_id(circuitpy, bootloader, board_id)

    new_version = circfirm.backend.s3.get_latest_board_version(
        board_id, language, pre_release
    )
    if packaging.version.Version(current_version) >= packaging.version.Version(
        new_version
    ):
        click.echo(
            f"Current version ({current_version}) is at or higher than proposed new update ({new_version})"
        )
        return

    circfirm.cli.ensure_bootloader_mode(bootloader)
    circfirm.cli.download_if_needed(board_id, new_version, language)
    circfirm.cli.copy_cache_firmware(board_id, new_version, language, bootloader)
