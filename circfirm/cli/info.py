# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for info subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device
import circfirm.cli


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument("device-path")
def cli(ctx: click.Context, device_path: str) -> None:
    """Check the information about the selected board."""
    circuitpys, _ = circfirm.cli.get_connection_statuses()
    if not circuitpys:
        raise click.ClickException(
            "Board must be in CIRCUITPY mode in order to detect board information"
        )
    if ctx.invoked_subcommand is None:
        name, version = circfirm.backend.device.get_board_info_from_circuitpy(
            device_path
        )
        click.echo(f"{name} ({version})")


@cli.command(name="board-id")
@click.pass_context
def info_board_ids(ctx: click.Context) -> None:
    """Get the board ID of the selected board."""
    device_path = ctx.parent.params["device_path"]
    info = circfirm.backend.device.get_board_info_from_circuitpy(device_path)
    click.echo(info[0])


@cli.command(name="version")
@click.pass_context
def info_versions(ctx: click.Context) -> None:
    """Get the CircuitPython version of the selected board."""
    device_path = ctx.parent.params["device_path"]
    info = circfirm.backend.device.get_board_info_from_circuitpy(device_path)
    click.echo(info[1])
