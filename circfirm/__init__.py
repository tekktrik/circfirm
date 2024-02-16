# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Shared functionality for the tool.

Author(s): Alec Delaney
"""

from typing import Any, Union

import yaml

from circfirm.startup import setup_file, setup_folder

# Folders
APP_DIR = setup_folder("circfirm")
UF2_ARCHIVE = setup_folder(APP_DIR, "archive")

# Files
MOUNT_LIST = setup_file(APP_DIR, "mountable.txt")
SETTINGS_FILE = setup_file(APP_DIR, "settings.yaml")

UF2INFO_FILE = "info_uf2.txt"
BOOTOUT_FILE = "boot_out.txt"


def get_setting(*settings_path: Union[str, int]) -> Any:
    """Get a setting."""
    with open(SETTINGS_FILE, encoding="utf-8") as setfile:
        settings = yaml.safe_load(setfile)
        for setting_opt in settings_path:
            settings = settings[setting_opt]
        return settings
