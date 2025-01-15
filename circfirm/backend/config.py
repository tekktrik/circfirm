# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""General configuration settings support functionality.

Author(s): Alec Delaney
"""

from typing import Any, Union

import yaml
from typing_extensions import TypeAlias

_YAML_SCALAR_T: TypeAlias = Union[str, int, float, bool]
_YAML_DICT_T: TypeAlias = dict[str, "_YAML_NODE_T"]
_YAML_LIST_T: TypeAlias = list["_YAML_NODE_T"]
_YAML_NODE_T: TypeAlias = Union[_YAML_SCALAR_T, _YAML_DICT_T, _YAML_LIST_T]

_VALID_TRUE_OPTIONS = ("y", "yes", "true", "1")
_VALID_FALSE_OPTIONS = ("n", "no", "false", "0")


def get_config_settings(settings_filepath: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Get the contents of a configuration settings file."""
    with open(settings_filepath, encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    with open(settings_filepath, encoding="utf-8") as yamlfile:
        types = yaml.safe_load(yamlfile)
    return settings, types


def is_node_scalar(value: _YAML_NODE_T) -> bool:
    """Check whether a node is a scalar."""
    return isinstance(value, (str, int, float, bool))


def is_input_bool(value: str) -> bool:
    """Check whether a node is a bool."""
    bool_options = _VALID_TRUE_OPTIONS + _VALID_FALSE_OPTIONS
    return value.lower() in bool_options


def cast_input_to_bool(value: str) -> bool:
    """Cast the value as a boolean."""
    if value.lower() in _VALID_TRUE_OPTIONS:
        return True
    if value.lower() in _VALID_FALSE_OPTIONS:
        return False
    raise ValueError(f'"{value}" could not be cast as a boolean')


def cast_input_to_int(value: str):
    """Cast the value as an integer."""
    try:
        return int(value)
    except ValueError as err:
        raise ValueError(f'"{value}" could not be cast as an integer') from err


def cast_input_to_float(value: str):
    """Cast the value as a floating point."""
    try:
        return float(value)
    except ValueError as err:
        raise ValueError(f'"{value}" could not be cast as a floating point') from err
