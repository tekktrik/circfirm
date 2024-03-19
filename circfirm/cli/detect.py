# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
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
    circuitpy = circfirm.backend.device.find_circuitpy()
    if not circuitpy:
        click.echo("No board connected in CIRCUITPY or equivalent mode")
        return
    click.echo(circuitpy)


@cli.command(name="bootloader")
def detect_bootloader() -> None:
    """Detect a connected board in bootloader mode."""
    bootloader = circfirm.backend.device.find_bootloader()
    if not bootloader:
        click.echo("No board connected in bootloader mode")
        return
    click.echo(bootloader)
