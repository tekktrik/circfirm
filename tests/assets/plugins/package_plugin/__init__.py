# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""A test module plugin.

Author(s): Alec Delaney
"""

import click

import package_plugin.extra


@click.command(name="packp")
def cli() -> None:
    """Utilize a local package plugin that will be loaded."""
    click.echo("This is from a local module plugin!")
    package_plugin.extra.print_text()
