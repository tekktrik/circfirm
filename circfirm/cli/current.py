# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the current subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend
import circfirm.cli


@click.command()
@click.option("-n", "--name", is_flag=True, default=False, help="Print the board name")
@click.option(
    "-v", "--version", is_flag=True, default=False, help="Print the firmware version"
)
def cli(name: bool, version: bool) -> None:
    """Check the information about the currently connected board."""
    circuitpy, _ = circfirm.cli.get_connection_status()
    if not circuitpy:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )
    board_name, firmware_version = circfirm.backend.get_board_info(circuitpy)
    if not any(name, version):
        name = version = True
    if name:
        click.echo(f"Board Name: {board_name}")
    if version:
        click.echo(f"CircuitPython: {firmware_version}")
