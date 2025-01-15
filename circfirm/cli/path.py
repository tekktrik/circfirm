# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the paths subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm


@click.group()
def cli() -> None:
    """See filepaths for files and folders used by circfirm."""


@cli.command(name="config")
def path_config() -> None:
    """Get the configuration settings filepath."""
    click.echo(circfirm.SETTINGS_FILE)


@cli.command(name="local-plugins")
def path_local_plugins() -> None:
    """Get the local plugins folder filepath."""
    click.echo(circfirm.LOCAL_PLUGINS)


@cli.command(name="archive")
def path_archive() -> None:
    """Get the firmware archive folder filepath."""
    click.echo(circfirm.UF2_ARCHIVE)
