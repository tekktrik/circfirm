# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the CLI's general functionality.

Author(s): Alec Delaney
"""

import importlib
import sys
from typing import Callable, TypeVar

import pytest
from click.testing import CliRunner

import circfirm.cli
import tests.assets.plugins.missing_plugin
import tests.helpers

_T = TypeVar("_T")

RUNNER = CliRunner()


@tests.helpers.with_local_plugins(
    ["examples/plugins/module_plugin.py", "examples/plugins/package_plugin"]
)
def test_load_local_plugins() -> None:
    """Tests loading local plugins."""
    importlib.reload(circfirm.cli)
    result = RUNNER.invoke(circfirm.cli.cli, ["--help"])
    assert result.exit_code == 0
    assert result.output == tests.helpers.get_help_response(
        ["module_plugin.py", "package_plugin"]
    )


def test_load_local_plugin_missing_cli() -> None:
    """Tests loading local plugins that don't have `cli()` entries."""
    with pytest.raises(RuntimeError):
        circfirm.cli.load_cmd_from_module(
            tests.assets.plugins.missing_plugin,
            "doesnotexist",
            ignore_missing_entry=False,
        )


@tests.helpers.with_downloaded_plugins(["circfirm_hello_world"])
def test_load_downloaded_plugins() -> None:
    """Tests loading downloaded plugins."""
    result = RUNNER.invoke(circfirm.cli.cli, ["--help"])
    assert result.exit_code == 0
    assert result.output == tests.helpers.get_help_response(
        downloaded_plugins=["circfirm_hello_world"]
    )


@tests.helpers.with_downloaded_plugins(["doesnotexist"])
def test_load_downloaded_plugin_missing() -> None:
    """Tests loading a missing downloaded plugin."""
    result = RUNNER.invoke(circfirm.cli.cli, ["--help"])
    assert result.exit_code == 0
    assert result.output == tests.helpers.get_help_response()
