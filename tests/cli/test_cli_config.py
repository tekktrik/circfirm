# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's config command functionality.

Author(s): Alec Delaney
"""

import os

import yaml
from click.testing import CliRunner

import circfirm
import circfirm.cli.config
import tests.helpers
from circfirm.cli import cli

RUNNER = CliRunner()

DEFAULT_SETTINGS = "tests/assets/settings/settings.yaml"


name_of = lambda x: f"{x.__name__}"


def get_printed_default_settings() -> str:
    """Get the default (template) settings as printed."""
    with open(DEFAULT_SETTINGS, encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    return yaml.safe_dump(settings, indent=4)


@tests.helpers.with_config_settings
def test_config_view_all() -> None:
    """Tests the config view command."""
    expected_output = get_printed_default_settings()
    result = RUNNER.invoke(cli, ["config", "view"])
    assert result.exit_code == 0
    assert result.output == expected_output


@tests.helpers.with_config_settings
def test_config_view_nonscalar() -> None:
    """Tests viewing a non-scalar type setting."""
    non_scalar_key = "typed_lists"
    with open(DEFAULT_SETTINGS, encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    printed_settings = yaml.safe_dump(settings[non_scalar_key], indent=4)
    result = RUNNER.invoke(cli, ["config", "view", non_scalar_key])
    assert result.exit_code == 0
    assert result.output == printed_settings


@tests.helpers.with_config_settings
def test_config_view_specific() -> None:
    """Tests viewing specific setting."""
    scalar_types = (str, int, float, bool)
    scalar_values = ("This is text", "123", "0.123", "true")
    for scalar_type, scalar_value in zip(scalar_types, scalar_values):
        result = RUNNER.invoke(cli, ["config", "view", name_of(scalar_type)])
        assert result.exit_code == 0
        assert result.output == f"{scalar_value}\n"

    result = RUNNER.invoke(cli, ["config", "view", "dict.int"])
    assert result.exit_code == 0
    assert result.output == "789\n"


@tests.helpers.with_config_settings
def test_config_view_nonexistent() -> None:
    """Tests viewing non-existent setting."""
    result = RUNNER.invoke(cli, ["config", "view", "doesnotexist"])
    assert result.exit_code != 0


def test_config_reset() -> None:
    """Tests the reseting of the config settings file."""
    template_filepath = os.path.join("circfirm", "templates", "settings.yaml")
    with open(template_filepath, encoding="utf-8") as templatefile:
        expected_settings = templatefile.read()
    result = RUNNER.invoke(cli, ["config", "reset"])
    assert result.exit_code == 0
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
        actual_settings = setfile.read()
    assert actual_settings == expected_settings


@tests.helpers.with_config_settings
def test_config_path() -> None:
    """Tests printing the configuration setting path."""
    result = RUNNER.invoke(cli, ["config", "path"])
    assert result.exit_code == 0
    assert result.output == f"{circfirm.SETTINGS_FILE}\n"
