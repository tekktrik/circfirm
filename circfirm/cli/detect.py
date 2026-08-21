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
    click.echo("\n".join(circuitpys))


@cli.command(name="bootloader")
def detect_bootloader() -> None:
    """Detect a connected board in bootloader mode."""
    bootloaders = circfirm.backend.device.find_bootloaders()
    if not bootloaders:
        click.echo("No board connected in bootloader mode")
        return
    click.echo("\n".join(bootloaders))
