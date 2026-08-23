# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the current subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device
import circfirm.cli


def get_board_info() -> list[tuple[str, str]]:
    """Get board info via the CLI."""
    circuitpys, _ = circfirm.cli.get_connection_statuses()
    if not circuitpys:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )

    board_infos = []
    for circuitpy in circuitpys:
        board_info = circfirm.backend.device.get_board_info(circuitpy)
        board_infos.append(board_info)
    return board_infos


@click.group()
def cli() -> None:
    """Check the information about the currently connected board."""


@cli.command(name="board-id")
def current_board_id() -> None:
    """Get the board ID of the currently connected board."""
    board_infos = get_board_info()
    for board_info in board_infos:
        click.echo(board_info[0])


@cli.command(name="version")
def current_version() -> None:
    """Get the CircuitPython version of the currently connected board."""
    board_infos = get_board_info()
    for board_info in board_infos:
        click.echo(board_info[1])
