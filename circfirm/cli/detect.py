# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the detect subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device


@click.group()
def cli() -> None:
    """Detect connected CircuitPython boards."""


@cli.command(name="circuitpy")
def detect_circuitpy() -> None:
    """Detect a connected board in CIRCUITPY or equivalent mode."""
    circuitpys = circfirm.backend.device.find_circuitpys()

    if not circuitpys:
        click.echo("No board connected in CIRCUITPY or equivalent mode")
        return

    for device_path in sorted(circuitpys):
        name, version = circfirm.backend.device.get_board_info_from_circuitpy(
            device_path
        )
        formatted = circfirm.cli.format_circuitpy_info(device_path, name, version)
        click.echo(formatted)


@cli.command(name="bootloader")
def detect_bootloader() -> None:
    """Detect a connected board in bootloader mode."""
    bootloaders = circfirm.backend.device.find_bootloaders()

    if not bootloaders:
        click.echo("No board connected in bootloader mode")
        return

    for device_path in sorted(bootloaders):
        formatted = circfirm.cli.format_bootloader_info(device_path)
        click.echo(formatted)
