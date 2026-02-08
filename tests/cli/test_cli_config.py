# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Tests the CLI's config command functionality.

Author(s): Alec Delaney
"""

from unittest import mock

import click
from click.testing import CliRunner

import circfirm
from circfirm.cli import cli

RUNNER = CliRunner()


def get_printed_default_settings() -> None:
    """Get the default (template) settings as printed."""
    with open("circfirm/templates/settings.yaml", encoding="utf-8") as yamlfile:
        return yamlfile.read()


def test_config_view_and_edit(mock_default_config: None) -> None:
    """Tests writing and reading the same config setting."""
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "true"])
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "true\n"

    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "false"])
    result = RUNNER.invoke(cli, ["config", "view", "output.supporting.silence"])
    assert result.exit_code == 0
    assert result.output == "false\n"


def test_config_view(mock_default_config: None) -> None:
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


def test_config_edit(mock_default_config: None) -> None:
    """Tests the config edit command."""
    # Test writing a non-existent setting
    result = RUNNER.invoke(cli, ["config", "edit", "doesnotexist", "123"])
    assert result.exit_code != 0

    # Test writing to setting tree
    result = RUNNER.invoke(cli, ["config", "edit", "output", "123"])
    assert result.exit_code != 0

    # Test writing bad type
    RUNNER.invoke(cli, ["config", "edit", "output.supporting.silence", "123"])
    assert result.exit_code != 0


def test_config_edit_setting_only(mock_default_config: None) -> None:
    """Tests the config edit command with only a setting argument."""
    result = RUNNER.invoke(cli, ["config", "edit", "somesetting"])
    assert result.exit_code != 0


def test_config_edit_editor(mock_default_config: None) -> None:
    """Tests the config edit command to use an editor."""
    with mock.patch("click.edit") as mock_click_edit:
        result = RUNNER.invoke(cli, ["config", "edit"])
        assert result.exit_code == 0
        mock_click_edit.assert_called_once_with(
            filename=circfirm.SETTINGS_FILE, editor=None
        )


def test_config_edit_editor_bad_option(mock_default_config: None) -> None:
    """Tests the config edit command to use a non-existent editor."""
    bad_editor = "doesnotexist"
    result = RUNNER.invoke(cli, ["config", "edit", "editor", bad_editor])
    assert result.exit_code == 0
    with mock.patch("click.edit") as mock_click_edit:
        mock_click_edit.side_effect = click.ClickException("Example failure")
        result = RUNNER.invoke(cli, ["config", "edit"])
        assert result.exit_code != 0
        mock_click_edit.assert_called_once_with(
            filename=circfirm.SETTINGS_FILE, editor=bad_editor
        )


def test_config_path(mock_default_config: None) -> None:
    """Tests the config command for returning the path to the settings file."""
    result = RUNNER.invoke(cli, ["config", "path"])
    assert result.exit_code == 0
    assert result.output == f"{circfirm.SETTINGS_FILE}\n"


def test_config_reset(mock_default_config: None) -> None:
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
