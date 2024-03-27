# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# Based on code from circlink (Authored by Alec Delaney, licensed under MIT license)
#
# SPDX-License-Identifier: MIT

"""CLI functionality for the config subcommand.

Author(s): Alec Delaney
"""

import os
from typing import Dict, List, Union

import click
import yaml
from typing_extensions import TypeAlias

import circfirm
import circfirm.cli
import circfirm.startup

_YAML_SCALAR_T: TypeAlias = Union[str, int, float, bool]
_YAML_DICT_T: TypeAlias = Dict[str, "_YAML_NODE_T"]
_YAML_LIST_T: TypeAlias = List["_YAML_NODE_T"]
_YAML_NODE_T: TypeAlias = Union[_YAML_SCALAR_T, _YAML_DICT_T, _YAML_LIST_T]

_VALID_TRUE_OPTIONS = ("y", "yes", "true", "1")
_VALID_FALSE_OPTIONS = ("n", "no", "false", "0")


def _is_node_scalar(value: _YAML_NODE_T) -> bool:
    """Check whether a node is a scalar."""
    return isinstance(value, (str, int, float, bool))


def _is_input_bool(value: str) -> bool:
    """Check whether a node is a bool."""
    bool_options = _VALID_TRUE_OPTIONS + _VALID_FALSE_OPTIONS
    return value.lower() in bool_options


def _is_input_int(value: str) -> bool:
    """Check whether a node is an integer."""
    try:
        _ = int(value)
        return True
    except ValueError:
        return False


def _is_input_float(value: str) -> bool:
    """Check whether a node is a floating point."""
    try:
        _ = float(value)
        return True
    except ValueError:
        return False


def _cast_input_to_bool(value: str) -> bool:
    """Cast the value as a boolean."""
    if value.lower() in _VALID_TRUE_OPTIONS:
        return True
    if value.lower() in _VALID_FALSE_OPTIONS:
        return False
    raise ValueError(f'"{value}" could not be cast as a boolean')


def _cast_input_to_int(value: str):
    """Cast the value as an integer."""
    try:
        return int(value)
    except ValueError as err:
        raise ValueError(f'"{value}" could not be cast as an integer') from err


def _cast_input_to_float(value: str):
    """Cast the value as a floating point."""
    try:
        return float(value)
    except ValueError as err:
        raise ValueError(f'"{value}" could not be cast as a floating point') from err


@click.group()
def cli():
    """View and update the configuration settings for the circfirm CLI."""


@cli.command(name="view")
@click.argument("setting", default="all")
def config_view(setting: str) -> None:
    """View a config setting."""
    # Get the settings, show all settings if no specific on is specified
    settings = circfirm.cli.get_settings()
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

    if not _is_node_scalar(value):
        click.echo(yaml.safe_dump(value, indent=4), nl=False)
        return

    # Show the specified setting
    if isinstance(value, bool):
        value = str(value).lower()
    click.echo(value)


@cli.command(name="edit")
@click.argument("setting")
@click.argument("value")
def config_edit(
    setting: str,
    value: str,
) -> None:
    """Update a config setting."""
    # Get the settings, use another reference to parse
    orig_settings = circfirm.cli.get_settings()
    target_schema = circfirm.cli.get_settings_schema()
    target_setting = orig_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and set it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
            target_schema = target_schema[extra_arg]
        target_value = target_schema[config_args[-1]]
        target_value_type = type(target_value)
        if not _is_node_scalar(target_value):
            raise click.ClickException(
                "Cannot change this setting, please change the sub-settings within it"
            )
        if target_value_type == bool:
            if not _is_input_bool(value):
                raise TypeError
            target_setting[config_args[-1]] = _cast_input_to_bool(value)
        elif target_value_type == int:
            if not _is_input_int(value):
                raise TypeError
            target_setting[config_args[-1]] = _cast_input_to_int(value)
        elif target_value_type == float:
            if not _is_input_float(value):
                raise TypeError
            target_setting[config_args[-1]] = _cast_input_to_float(value)
        else:
            target_setting[config_args[-1]] = value
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except TypeError:
        raise click.ClickException(
            f"Cannot use the given value for this setting, must be of type {target_value_type.__name__}"
        )

    # Write the settings back to the file
    with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


@cli.command(name="add")
@click.argument("setting")
@click.argument("value")
def config_add(setting: str, value: str) -> None:
    """Add a value to a list."""
    # Get the settings, use another reference to parse
    orig_settings = circfirm.cli.get_settings()
    target_schema = circfirm.cli.get_settings_schema()
    target_setting = orig_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and add it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
            target_schema = target_schema[extra_arg]
        editing_list: List = target_setting[config_args[-1]]
        target_type = type(editing_list)
        if target_type in (dict, str, int, float, bool):
            raise click.ClickException("Cannot add items to this setting")
        schema_list: List = target_schema[config_args[-1]]
        element_type = type(schema_list[0])
        if element_type == dict:
            raise click.ClickException("Cannot add items to lists of dictionaries")
        if element_type == bool:
            editing_list.append(_cast_input_to_bool(value))
        elif element_type == int:
            editing_list.append(_cast_input_to_int(value))
        elif element_type == float:
            editing_list.append(_cast_input_to_float(value))
        else:
            editing_list.append(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except ValueError:
        raise click.ClickException(
            f"Cannot add the given value for this setting, must be of type {element_type.__name__}"
        )

    # Write the settings back to the file
    with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


@cli.command(name="remove")
@click.argument("setting")
@click.argument("value")
def config_remove(setting: str, value: str) -> None:
    """Remove a value from a list."""
    # Get the settings, use another reference to parse
    orig_settings = circfirm.cli.get_settings()
    target_schema = circfirm.cli.get_settings_schema()
    target_setting = orig_settings

    config_args = setting.split(".")

    # Attempt to parse for the specified config setting and remove it
    try:
        for extra_arg in config_args[:-1]:
            target_setting = target_setting[extra_arg]
            target_schema = target_schema[extra_arg]
        editing_list: List = target_setting[config_args[-1]]
        target_type = type(editing_list)
        if target_type in (dict, str, int, float, bool):
            raise click.ClickException("Cannot remove items from this setting")
        schema_list: List = target_schema[config_args[-1]]
        element_type = type(schema_list[0])
        if element_type == dict:
            raise click.ClickException(
                "Cannot remove items from dictionaries via the command line"
            )
        if element_type == bool:
            editing_list.remove(_cast_input_to_bool(value))
        elif element_type == int:
            editing_list.remove(_cast_input_to_int(value))
        elif element_type == float:
            editing_list.remove(_cast_input_to_float(value))
        else:
            editing_list.remove(value)
    except KeyError:
        raise click.ClickException(f"Setting {setting} does not exist")
    except ValueError:
        raise click.ClickException(f"{value} was not located in the given list")

    # Write the settings back to the file
    with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as yamlfile:
        yaml.safe_dump(orig_settings, yamlfile)


@cli.command(name="editor")
def config_editor() -> None:  # pragma: no cover
    """Edit the configuration file in an editor."""
    settings = circfirm.cli.get_settings()
    editor = settings["editor"]
    editor = editor if editor else None
    try:
        click.edit(filename=circfirm.SETTINGS_FILE, editor=editor)
    except click.ClickException as err:
        raise click.ClickException(
            f'{editor} is not a path to a valid editor, use `circfirm config edit editor ""` to set to default.'
        ) from err


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
