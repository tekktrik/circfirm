# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's config command functionality.

Author(s): Alec Delaney
"""

import os
from typing import List

import yaml
from click.testing import CliRunner

import circfirm
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()

DEFAULT_SETTINGS = "tests/assets/settings/settings.yaml"


name_of = lambda x: f"{x.__name__}"
error_for = (
    lambda x: f"Error: Cannot use the given value for this setting, must be of type {name_of(x)}\n"
)

SCALAR_TYPES = (str, int, float, bool)
SCALAR_VALUES = ("This is text", "123", "0.123", "true")
NEW_SCALAR_VALUES = ("value", "234", "0.234", "false")


def get_printed_default_settings() -> str:
    """Get the default (template) settings as printed."""
    with open(DEFAULT_SETTINGS, encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    return yaml.safe_dump(settings, indent=4)


@tests.helpers.with_mock_config_settings
def test_config_view_all() -> None:
    """Tests viewing all settings."""
    expected_output = get_printed_default_settings()

    # Test viewing all settings
    result = RUNNER.invoke(cli, ["config", "view"])
    assert result.exit_code == 0
    assert result.output == expected_output


@tests.helpers.with_mock_config_settings
def test_config_view_specific() -> None:
    """Tests viewing specific setting."""
    for scalar_type, scalar_value in zip(SCALAR_TYPES, SCALAR_VALUES):
        result = RUNNER.invoke(cli, ["config", "view", name_of(scalar_type)])
        assert result.exit_code == 0
        assert result.output == f"{scalar_value}\n"

    result = RUNNER.invoke(cli, ["config", "view", "dict.int"])
    assert result.exit_code == 0
    assert result.output == "789\n"


@tests.helpers.with_mock_config_settings
def test_config_view_nonscalar() -> None:
    """Tests viewing a non-scalar type setting."""
    non_scalar_key = "typed_lists"
    with open(DEFAULT_SETTINGS, encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    printed_settings = yaml.safe_dump(settings[non_scalar_key], indent=4)
    result = RUNNER.invoke(cli, ["config", "view", non_scalar_key])
    assert result.exit_code == 0
    assert result.output == printed_settings


@tests.helpers.with_mock_config_settings
def test_config_view_nonexistent() -> None:
    """Tests viewing non-existent setting."""
    result = RUNNER.invoke(cli, ["config", "view", "doesnotexist"])
    assert result.exit_code != 0


@tests.helpers.with_local_plugins(["examples/plugins/module_plugin.py"])
def test_config_view_plugin() -> None:
    """Tests seeing plugin settings."""
    result = RUNNER.invoke(cli, ["config", "view", "--plugin", "module_plugin"])
    assert result.exit_code == 0
    with open(
        "examples/plugins/module_plugin_settings.yaml", encoding="utf-8"
    ) as setfile:
        settings = yaml.safe_load(setfile)
    assert result.output == yaml.safe_dump(settings, indent=4)


@tests.helpers.with_local_plugins(["examples/plugins/module_plugin.py"])
def test_config_view_plugin_missing() -> None:
    """Tests seeing plugin settings."""
    result = RUNNER.invoke(cli, ["config", "view", "--plugin", "doesnotexist"])
    assert result.exit_code != 0
    assert (
        result.output
        == "Error: Unable to find the requested configuration settings file\n"
    )


@tests.helpers.with_mock_config_settings
def test_config_edit_specific() -> None:
    """Tests writing a setting."""
    for scalar_type, scalar_value in zip(SCALAR_TYPES, NEW_SCALAR_VALUES):
        result = RUNNER.invoke(
            cli, ["config", "edit", name_of(scalar_type), scalar_value]
        )
        assert result.exit_code == 0
        with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
            settings = yaml.safe_load(setfile)
        read_value = settings[name_of(scalar_type)]
        assert str(read_value).lower() == scalar_value


@tests.helpers.with_mock_config_settings
def test_config_edit_nonexistent() -> None:
    """Tests writing a non-existent setting."""
    result = RUNNER.invoke(cli, ["config", "edit", "doesnotexist", "123"])
    assert result.exit_code != 0


@tests.helpers.with_mock_config_settings
def test_config_edit_tree() -> None:
    """Tests writing to setting tree."""
    error_response = (
        "Error: Cannot change this setting, please change the sub-settings within it\n"
    )
    for value in ("dict", "list"):
        result = RUNNER.invoke(cli, ["config", "edit", value, "123"])
        assert result.exit_code != 0
        assert result.output == error_response


@tests.helpers.with_mock_config_settings
def test_config_edit_bad_type() -> None:
    """Tests writing bad type."""
    valid_types = SCALAR_TYPES[1:]
    for scalar_type in valid_types:
        result = RUNNER.invoke(cli, ["config", "edit", name_of(scalar_type), "xyz"])
        print(f"Checkking {scalar_type}")
        print(result.output)
        assert result.exit_code != 0
        assert result.output == error_for(scalar_type)


@tests.helpers.with_mock_config_settings
def test_config_add() -> None:
    """Tests add values to a configuration setting list."""
    with open(DEFAULT_SETTINGS, encoding="utf-8") as setfile:
        orig_settings = yaml.safe_load(setfile)
    new_value = "D"
    test_key = f"typed_lists.list_str"
    result = RUNNER.invoke(cli, ["config", "add", test_key, new_value])
    assert result.exit_code == 0
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
        new_settings = yaml.safe_load(setfile)
    parent_key, type_key = test_key.split(".")
    assert new_settings[parent_key][type_key] == orig_settings[parent_key][type_key] + [
        new_value
    ]


@tests.helpers.with_mock_config_settings
def test_config_add_to_scalar() -> None:
    """Tests attempting to add to a scalar."""
    for setting_type in SCALAR_TYPES:
        test_key = f"{name_of(setting_type)}"
        result = RUNNER.invoke(cli, ["config", "add", test_key, "value"])
        assert result.exit_code != 0
        assert result.output == "Error: Cannot add items to this setting\n"


@tests.helpers.with_mock_config_settings
def test_config_add_to_dict() -> None:
    """Tests attempting to add to a dict."""
    result = RUNNER.invoke(cli, ["config", "add", "dict", "value"])
    assert result.exit_code != 0
    assert result.output == "Error: Cannot add items to this setting\n"


@tests.helpers.with_mock_config_settings
def test_config_add_to_list_dict() -> None:
    """Tests attempting to add to a list of dicts."""
    result = RUNNER.invoke(cli, ["config", "add", "typed_lists.list_dict", "value"])
    assert result.exit_code != 0
    assert result.output == "Error: Cannot add items to lists of dictionaries\n"


@tests.helpers.with_mock_config_settings
def test_config_add_nonexistent() -> None:
    """Tests attempting to add to a non-existent setting."""
    setting_name = "doesnotexist"
    result = RUNNER.invoke(cli, ["config", "add", setting_name, "value"])
    assert result.exit_code != 0
    assert result.output == f"Error: Setting {setting_name} does not exist\n"


@tests.helpers.with_mock_config_settings
def test_config_add_empty_list() -> None:
    """Tests attempting to add to an empty list."""
    key = "empty_list"
    value = "newentry"
    result = RUNNER.invoke(cli, ["config", "add", key, value])
    assert result.exit_code == 0
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
        settings = yaml.safe_load(setfile)
    assert settings[key] == [value]


@tests.helpers.with_mock_config_settings
def test_config_remove() -> None:
    """Tests removing items from a list."""
    with open(DEFAULT_SETTINGS, encoding="utf-8") as setfile:
        orig_settings = yaml.safe_load(setfile)
    remove_value = "B"
    test_key = f"typed_lists.list_str"
    result = RUNNER.invoke(cli, ["config", "remove", test_key, remove_value])
    assert result.exit_code == 0
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
        new_settings = yaml.safe_load(setfile)
    parent_key, type_key = test_key.split(".")
    modified_list: list[str] = orig_settings[parent_key][type_key]
    modified_list.remove(remove_value)
    assert new_settings[parent_key][type_key] == modified_list


@tests.helpers.with_mock_config_settings
def test_config_remove_from_scalar() -> None:
    """Tests attempting to remove from a scalar."""
    for setting_type in SCALAR_TYPES:
        test_key = f"{name_of(setting_type)}"
        result = RUNNER.invoke(cli, ["config", "remove", test_key, "value"])
        assert result.exit_code != 0
        assert result.output == "Error: Cannot remove items from this setting\n"


@tests.helpers.with_mock_config_settings
def test_config_remove_from_dict() -> None:
    """Tests attempting to remove from a dict."""
    result = RUNNER.invoke(cli, ["config", "remove", "dict", "value"])
    assert result.exit_code != 0
    assert result.output == "Error: Cannot remove items from this setting\n"


@tests.helpers.with_mock_config_settings
def test_config_remove_from_list_dict() -> None:
    """Tests attempting to remove from a list of dicts."""
    result = RUNNER.invoke(cli, ["config", "remove", "typed_lists.list_dict", "value"])
    assert result.exit_code != 0
    assert result.output == "Error: Cannot remove items from lists of dictionaries\n"


@tests.helpers.with_mock_config_settings
def test_config_remove_nonexistent() -> None:
    """Tests attempting to remove from a non-existent setting."""
    setting_name = "doesnotexist"
    result = RUNNER.invoke(cli, ["config", "remove", setting_name, "value"])
    assert result.exit_code != 0
    assert result.output == f"Error: Setting {setting_name} does not exist\n"


@tests.helpers.with_mock_config_settings
def test_config_remove_not_found() -> None:
    """Tests attempting to remove an item not contained in a list."""
    value = "value"
    result = RUNNER.invoke(cli, ["config", "remove", "typed_lists.list_str", value])
    assert result.exit_code != 0
    assert result.output == f"Error: {value} was not located in the given list\n"


@tests.helpers.with_mock_config_settings
def test_config_remove_empty_list() -> None:
    """Tests attempting to remove from an empty list."""
    result = RUNNER.invoke(cli, ["config", "remove", "empty_list", "value"])
    assert result.exit_code != 0
    assert result.output == f"Error: No items are contained in the given list\n"


@tests.helpers.with_mock_config_settings
def test_config_path() -> None:
    """Tests printing the configuration setting path."""
    result = RUNNER.invoke(cli, ["config", "path"])
    assert result.exit_code == 0
    assert result.output == f"{circfirm.SETTINGS_FILE}\n"


@tests.helpers.with_mock_config_settings
def test_config_path_missing_plugin() -> None:
    """Tests printing the configuration setting path."""
    plugin = "doesnotexist"
    result = RUNNER.invoke(cli, ["config", "path", "--plugin", "doesnotexist"])
    assert result.exit_code == 0
    assert result.output == f"No standard settings file exists for {plugin}\n"


@tests.helpers.with_mock_config_settings
def test_config_reset() -> None:
    """Tests reseting the config settings file."""
    template_filepath = os.path.join("circfirm", "templates", "settings.yaml")
    with open(template_filepath, encoding="utf-8") as templatefile:
        expected_settings = templatefile.read()
    result = RUNNER.invoke(cli, ["config", "reset"])
    assert result.exit_code == 0
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
        actual_settings = setfile.read()
    assert actual_settings == expected_settings


@tests.helpers.with_mock_config_settings
def test_config_reset_missing_plugin() -> None:
    """Tests reseting a plugin's config settings file."""
    result = RUNNER.invoke(cli, ["config", "reset", "--plugin", "doesnotexist"])
    assert result.exit_code != 0
    assert (
        result.output
        == "Error: The default configuration file could not be located, reset not performed\n"
    )
