# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the about subcommand.

Author(s): Alec Delaney
"""

import click


@click.command()
def cli() -> None:
    """Information about circfirm."""
    click.echo("Written by Alec Delaney, licensed under MIT License.")
