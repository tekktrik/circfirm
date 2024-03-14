# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the current subcommand.

Author(s): Alec Delaney
"""

from typing import Tuple

import click

import circfirm.backend.device
import circfirm.cli


def get_board_info() -> Tuple[str, str]:
    """Get board info via the CLI."""
    circuitpy, _ = circfirm.cli.get_connection_status()
    if not circuitpy:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )
    return circfirm.backend.device.get_board_info(circuitpy)


@click.group()
def cli() -> None:
    """Check the information about the currently connected board."""


@cli.command(name="board-id")
def current_board_id() -> None:
    """Get the board ID of the currently connected board."""
    click.echo(get_board_info()[0])


@cli.command(name="version")
def current_version() -> None:
    """Get the CircuitPython version of the currently connected board."""
    click.echo(get_board_info()[1])
