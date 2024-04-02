# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Plugin support functionality.

Author(s): Alec Delaney
"""

import os
import shutil
from typing import Any, Dict, Optional

import yaml

import circfirm
import circfirm.backend.config
import circfirm.startup


def uninstall_plugin_settings(name: str) -> None:
    """Uninstall plugin settings."""
    plugin_settings_folder = os.path.join(circfirm.PLUGIN_SETTINGS, name)
    dest = os.path.join(plugin_settings_folder, "settings.yaml")
    plugin = None
    for plugin_info in circfirm.startup.TEMPLATE_LIST:
        if plugin_info[1] == dest:
            plugin = plugin_info
            break
    if plugin:
        templates = set(circfirm.startup.TEMPLATE_LIST)
        circfirm.startup.TEMPLATE_LIST = list(templates - set([plugin]))
    if os.path.exists(plugin_settings_folder):
        shutil.rmtree(plugin_settings_folder)


def ensure_plugin_settings(name: str, settings_path: str) -> None:
    """Ensure a plugin's settings are installed."""
    plugin_settings_folder = os.path.join(circfirm.PLUGIN_SETTINGS, name)
    if not os.path.exists(plugin_settings_folder):
        os.mkdir(plugin_settings_folder)
    template_args = settings_path, os.path.join(plugin_settings_folder, "settings.yaml")
    circfirm.startup.specify_template(*template_args)
    circfirm.startup.ensure_template(*template_args)


def _get_settings_file(name: str, extension: str) -> Optional[str]:
    """Locate a specific configuration file based on extension."""
    plugin_settings_folder = os.path.join(circfirm.PLUGIN_SETTINGS, name)
    settings_file = os.path.join(plugin_settings_folder, f"settings.{extension}")
    with open(settings_file, encoding="utf-8") as setfile:
        return yaml.safe_load(setfile)


def get_settings(name: str) -> Dict[str, Any]:
    """Get the contents of the settings file."""
    return _get_settings_file(name, "yaml")


def get_plugin_settings_path(name: str) -> str:
    """Get the path for the folder containing the settings file."""
    return os.path.join(circfirm.PLUGIN_SETTINGS, name)
