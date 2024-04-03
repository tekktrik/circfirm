# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend configuration file functionality.

Author(s): Alec Delaney
"""

import pathlib

import circfirm
import circfirm.plugins
import tests.helpers


@tests.helpers.with_local_plugins(["examples/plugins/module_plugin.py"])
def test_uninstall_plugin_settings() -> None:
    """Tests uninstalling a plugin's configuration settings file."""
    plugin_name = "module_plugin"
    plugin_folder = pathlib.Path(circfirm.PLUGIN_SETTINGS) / plugin_name
    settings_file = plugin_folder / "settings.yaml"
    assert settings_file.exists()
    assert settings_file.is_file()
    circfirm.plugins.uninstall_plugin_settings(plugin_name)
    assert not plugin_folder.exists()
