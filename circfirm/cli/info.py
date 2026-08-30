# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for info subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device
import circfirm.cli


@click.group()
def cli() -> None:
    """Check the information about the currently connected board."""
    circuitpys, _ = circfirm.cli.get_connection_statuses()
    if not circuitpys:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )


@cli.command(name="board-id")
@click.argument("device-path")
def current_board_ids(device_path: str) -> None:
    """Get the board ID of the currently connected board."""
    info = circfirm.backend.device.get_board_info_from_circuitpy(device_path)
    click.echo(info[0])


@cli.command(name="version")
@click.argument("device-path")
def current_versions(device_path: str) -> None:
    """Get the CircuitPython version of the currently connected board."""
    info = circfirm.backend.device.get_board_info_from_circuitpy(device_path)
    click.echo(info[1])
