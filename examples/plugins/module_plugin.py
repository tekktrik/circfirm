# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""A test module plugin.

Author(s): Alec Delaney
"""

import click

import circfirm.plugins

circfirm.plugins.ensure_plugin_settings(
    "module_plugin", "examples/plugins/module_plugin_settings.yaml"
)


@click.command(name="mod")
def cli() -> None:
    """Utilize a local module plugin that will be loaded."""
    click.echo("This is from a local module plugin!")
