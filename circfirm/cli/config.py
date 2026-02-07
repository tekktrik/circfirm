# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# Based on code from circlink (Authored by Alec Delaney, licensed under MIT license)
# SPDX-License-Identifier: MIT

"""CLI functionality for the config subcommand.

Author(s): Alec Delaney
"""

import os

import click
import yaml

import circfirm
import circfirm.cli
import circfirm.startup


@click.group()
def cli():
    """View and update the configuration settings for the circfirm CLI."""


@cli.command(name="view")
@click.argument("setting", default="")
def config_view(setting: str) -> None:
    """View a config setting."""
    # Get the settings, show all settings if no specific one is specified
    settings = circfirm.cli.get_settings()
    if not setting:
        click.echo(yaml.safe_dump(settings, indent=4))
        return

    # Get the specified settings
    config_args = setting.split(".")
    try:
        for extra_arg in config_args[:-1]:
            settings = settings[extra_arg]
        value = settings[config_args[-1]]
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")

    # Show the specified setting
    click.echo(yaml.safe_dump(value, indent=4))


@cli.command(name="edit")
@click.argument("setting", default="")
@click.argument("value", default="")
def config_edit(
    setting: str,
    value: str,
) -> None:
    """Update a config setting."""
    if setting and not value:
        raise click.ClickException(f"No value given for setting {setting}")

    # Get the settings, use another reference to parse
    orig_settings = circfirm.cli.get_settings()
    editor = orig_settings[
        "editor"
    ]  # TODO: Make standard warning for missing config options
    editor = editor if editor else None

    if not setting and not value:
        try:
            click.edit(filename=circfirm.SETTINGS_FILE, editor=editor)
        except click.ClickException as err:
            raise click.ClickException(
                f'{editor} is not a path to a valid editor, use `circfirm config edit editor ""` to set to default.'
            ) from err

    target_setting = orig_settings
    config_args = setting.split(".")

    # Handle bool conversions
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False

    # Attempt to parse for the specified config setting and set it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
        prev_value = target_setting[config_args[-1]]
        prev_value_type = type(prev_value)
        if prev_value_type == dict:
            raise ValueError
        if prev_value_type == bool and value not in (True, False):
            raise TypeError
        target_setting[config_args[-1]] = prev_value_type(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except TypeError:
        raise click.ClickException(
            f"Cannot use that value for this setting, must be of type {prev_value_type}"
        )
    except ValueError:
        raise click.ClickException(
            "Cannot change this setting, please change the sub-settings within it"
        )

    # Write the settings back to the file
    with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


@cli.command(name="path")
def config_path() -> None:
    """Print the path where the configuration file is stored."""
    click.echo(circfirm.SETTINGS_FILE)


@cli.command(name="reset")
def config_reset() -> None:
    """Reset the configuration file with the provided template."""
    os.remove(circfirm.SETTINGS_FILE)
    src, dest = [
        (src, dest)
        for src, dest in circfirm.startup.TEMPLATE_LIST
        if dest == circfirm.SETTINGS_FILE
    ][0]
    circfirm.startup.ensure_template(src, dest)
