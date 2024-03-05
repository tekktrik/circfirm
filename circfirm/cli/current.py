# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the current subcommand.

Author(s): Alec Delaney
"""

from typing import Tuple

import click

import circfirm.backend
import circfirm.cli


def get_board_info() -> Tuple[str, str]:
    """Get board info via the CLI."""
    circuitpy, _ = circfirm.cli.get_connection_status()
    if not circuitpy:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )
    return circfirm.backend.get_board_info(circuitpy)


@click.group()
def cli() -> None:
    """Check the information about the currently connected board."""


@cli.command(name="name")
def current_name() -> None:
    """Get the board name of the currently connected board."""
    click.echo(get_board_info()[0])


@cli.command(name="version")
def current_version() -> None:
    """Get the CircuitPython version of the currently connected board."""
    click.echo(get_board_info()[1])
