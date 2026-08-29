# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the detect subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device


def _detect_circuitpys(announce_none: bool = True) -> int:
    circuitpys = circfirm.backend.device.find_circuitpys()

    if not circuitpys and announce_none:
        click.echo("No board connected in CIRCUITPY or equivalent mode")
        return

    for device_path in sorted(circuitpys):
        name, version = circfirm.backend.device.get_board_info_from_circuitpy(
            device_path
        )
        formatted = circfirm.cli.format_circuitpy_info(device_path, name, version)
        click.echo(formatted)

    return len(circuitpys)


def _detect_bootloaders(announce_none: bool = True) -> int:
    bootloaders = circfirm.backend.device.find_bootloaders()

    if not bootloaders and announce_none:
        click.echo("No board connected in bootloader mode")
        return

    for device_path in sorted(bootloaders):
        formatted = circfirm.cli.format_bootloader_info(device_path)
        click.echo(formatted)

    return len(bootloaders)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Detect connected CircuitPython boards."""
    if ctx.invoked_subcommand is None:
        num_circuitpys = _detect_circuitpys(False)
        num_bootloaders = _detect_bootloaders(False)
        if not num_circuitpys and not num_bootloaders:
            click.echo("No boards connected in either CIRCUITPY or bootloader modes")


@cli.command(name="circuitpy")
def detect_circuitpys() -> None:
    """Detect connected boards in CIRCUITPY or equivalent mode."""
    _detect_circuitpys()


@cli.command(name="bootloaders")
def detect_bootloaders() -> None:
    """Detect connected boards in bootloader mode."""
    _detect_bootloaders()
