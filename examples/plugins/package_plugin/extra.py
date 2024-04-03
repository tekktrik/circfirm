# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Extra functionality.

Author(s): Alec Delaney
"""

import click


def print_text() -> None:
    """Print extra text."""
    click.echo("This is extra text!")
