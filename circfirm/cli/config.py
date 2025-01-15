# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# Based on code from circlink (Authored by Alec Delaney, licensed under MIT license)
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the config subcommand.

Author(s): Alec Delaney
"""

# TODO: Convert to using schema file for settings

import os
from typing import Any, Dict, List, Tuple

import click
import yaml

import circfirm
import circfirm.backend.config
import circfirm.cli
import circfirm.plugins
import circfirm.startup


def _get_config_settings(plugin: str = "") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    try:
        return (
            circfirm.plugins.get_settings(plugin)
            if plugin
            else circfirm.cli.get_settings()
        )
    except FileNotFoundError:
        raise click.ClickException(
            "Unable to find the requested configuration settings file"
        )


def _get_settings_filepath(plugin: str = "") -> str:
    if plugin:
        parent_folder = circfirm.plugins.get_plugin_settings_path(plugin)
        target_settings_file = os.path.join(parent_folder, "settings.yaml")
    else:
        target_settings_file = circfirm.SETTINGS_FILE
    return target_settings_file


@click.group()
def cli():
    """View and update the configuration settings for the circfirm CLI."""


# TODO: Modify for schema update
@cli.command(name="view")
@click.argument("setting", default="all")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_view(setting: str, plugin: str) -> None:
    """View a config setting."""
    # Get the settings, show all settings if no specific on is specified
    settings, _ = _get_config_settings(plugin)
    if setting == "all":
        click.echo(yaml.safe_dump(settings, indent=4), nl=False)
        return

    # Get the specified settings
    config_args = setting.split(".")
    try:
        for extra_arg in config_args[:-1]:
            settings = settings[extra_arg]
        value = settings[config_args[-1]]
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")

    if not circfirm.backend.config.is_node_scalar(value):
        click.echo(yaml.safe_dump(value, indent=4), nl=False)
        return

    # Show the specified setting
    if isinstance(value, bool):
        value = str(value).lower()
    click.echo(value)


# TODO: Modify for schema update
@cli.command(name="edit")
@click.argument("setting")
@click.argument("value")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_edit(
    setting: str,
    value: str,
    plugin: str,
) -> None:
    """Update a config setting."""
    # Get the settings, use another reference to parse
    orig_settings, _ = _get_config_settings(plugin)
    target_setting = orig_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and set it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
        target_value = target_setting[config_args[-1]]
        target_value_type = type(target_value)
        if not circfirm.backend.config.is_node_scalar(target_value):
            raise click.ClickException(
                "Cannot change this setting, please change the sub-settings within it"
            )
        if target_value_type == bool:
            if circfirm.backend.config.is_input_bool(value):
                value = circfirm.backend.config.cast_input_to_bool(value)
            else:
                raise ValueError
        target_setting[config_args[-1]] = target_value_type(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except ValueError:
        raise click.ClickException(
            f"Cannot use the given value for this setting, must be of type {target_value_type.__name__}"
        )

    # Write the settings back to the file
    target_file = _get_settings_filepath(plugin)
    with open(target_file, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


# TODO: Modify for schema update
@cli.command(name="add")
@click.argument("setting")
@click.argument("value")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_add(setting: str, value: str, plugin: str) -> None:
    """Add a value to a list."""
    # Get the settings, use another reference to parse
    orig_settings, types_settings = _get_config_settings(plugin)
    target_setting = orig_settings
    target_type = types_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and add it
    try:
        for extra_arg in config_args[:-1]:  # TODO: Explore the use of helper functions here, since reference is basically a pointer
            target_setting = target_setting[extra_arg]
            target_type = target_type[extra_arg]
        editing_list: List = target_setting[config_args[-1]]
        # TODO: Convert target_type to actual type using new helper function
        if type(editing_list) in (dict, str, int, float, bool):  # TODO: Should be isinstance
            raise click.ClickException("Cannot add items to this setting")
        target_list: List = target_setting[config_args[-1]]
        try:
            element_type = type(target_list[0])  # TODO: Should use type from schema
        except IndexError:
            element_type = str
        if element_type == dict:
            raise click.ClickException("Cannot add items to lists of dictionaries")
        editing_list.append(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")

    # Write the settings back to the file
    target_file = _get_settings_filepath(plugin)
    with open(target_file, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


# TODO: Modify for schema update
@cli.command(name="remove")
@click.argument("setting")
@click.argument("value")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_remove(setting: str, value: str, plugin: str) -> None:
    """Remove a value from a list."""
    # Get the settings, use another reference to parse
    orig_settings, _ = _get_config_settings(plugin)
    target_setting = orig_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and remove it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
        editing_list: List = target_setting[config_args[-1]]
        target_type = type(editing_list)
        if target_type in (dict, str, int, float, bool):
            raise click.ClickException("Cannot remove items from this setting")
        target_list: List = target_setting[config_args[-1]]
        try:
            element_type = type(target_list[0])
        except IndexError:
            raise click.ClickException("No items are contained in the given list")
        if element_type == dict:
            raise click.ClickException("Cannot remove items from lists of dictionaries")
        editing_list.remove(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except ValueError:
        raise click.ClickException(f"{value} was not located in the given list")

    # Write the settings back to the file
    target_file = _get_settings_filepath(plugin)
    with open(target_file, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


# TODO: Modify for schema update
@cli.command(name="editor")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_editor(plugin: str) -> None:  # pragma: no cover
    """Edit the configuration file in an editor."""
    settings, _ = _get_config_settings()
    editor = settings["editor"]
    editor = editor if editor else None
    target_file = _get_settings_filepath(plugin)
    try:
        click.edit(filename=target_file, editor=editor)
    except click.ClickException as err:
        raise click.ClickException(
            f'{editor} is not a path to a valid editor, use `circfirm config edit editor ""` to set to default.'
        ) from err


@cli.command(name="path")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_path(plugin: str) -> None:
    """Print the path where the configuration file is stored."""
    target_file = _get_settings_filepath(plugin)
    if os.path.exists(target_file):
        click.echo(target_file)
    else:
        click.echo(f"No standard settings file exists for {plugin}")


@cli.command(name="reset")
@click.option(
    "-p", "--plugin", default="", help="Configure a plugin instead of circfirm"
)
def config_reset(plugin: str) -> None:
    """Reset the configuration file with the provided template."""
    target_settings_file = _get_settings_filepath(plugin)
    try:
        os.remove(target_settings_file)
        src, dest = [
            (src, dest)
            for src, dest in circfirm.startup.TEMPLATE_LIST
            if dest == target_settings_file
        ][0]
    except (FileNotFoundError, IndexError):
        raise click.ClickException(
            "The default configuration file could not be located, reset not performed"
        )
    circfirm.startup.ensure_template(src, dest)
