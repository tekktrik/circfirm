# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's config command functionality.

Author(s): Alec Delaney
"""

import json

import yaml
from click.testing import CliRunner

from circfirm.cli import cli

RUNNER = CliRunner()


def get_printed_default_settings() -> None:
    """Get the default (template) settings as printed."""
    with open("circfirm/templates/settings.yaml", encoding="utf-8") as yamlfile:
        settings = yaml.safe_load(yamlfile)
    return f"{json.dumps(settings, indent=4)}\n"


def test_config() -> None:
    """Tests the config view command."""
    expected_output = get_printed_default_settings()

    # Test viewing all settings
    result = RUNNER.invoke(cli, ["config", "view"])
    assert result.exit_code == 0
    assert result.output == expected_output

    # Test viewing specific setting
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "false\n"

    # Test viewing non-existent setting
    result = RUNNER.invoke(cli, ["config", "view", "doesnotexist"])
    assert result.exit_code != 0

    # Test writing a setting
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "true\n"
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "false"])
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "false\n"

    # Test writing a non-existent setting
    result = RUNNER.invoke(cli, ["config", "edit", "doesnotexist", "123"])
    assert result.exit_code != 0

    # Test writing to setting tree
    result = RUNNER.invoke(cli, ["config", "edit", "output", "123"])
    assert result.exit_code != 0

    # Test writing bad type
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "123"])
    assert result.exit_code != 0


def test_config_reset() -> None:
    """Tests the reseting of the config settings file."""
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "true\n"

    expected_settings = get_printed_default_settings()

    result = RUNNER.invoke(cli, ["config", "reset"])
    result = RUNNER.invoke(cli, ["config", "view"])
    assert result.exit_code == 0
    assert result.output == expected_settings
