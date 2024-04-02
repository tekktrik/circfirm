# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""A test plugin that does not have a `cli()` entry.

Author(s): Alec Delaney
"""

import click


@click.command(name="missp")
def missing_plugin() -> None:
    """Utilize a plugin that will not be loaded."""
    click.echo("This shouldn't be accessible!")  # pragma: no cover
