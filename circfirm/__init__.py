# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Shared functionality for the tool.

Author(s): Alec Delaney
"""

import sys
from typing import Any, Set, Union

import yaml

from circfirm.startup import file, folder

# Folders
APP_DIR = folder("circfirm")
UF2_ARCHIVE = folder(APP_DIR, "archive")

# Files
MOUNT_LIST = file(APP_DIR, "mountable.txt")
SETTINGS_FILE = file(APP_DIR, "settings.yaml")

UF2INFO_FILE = "info_uf2.txt"


def get_setting(*settings_path: Union[str, int]) -> Any:
    """Get a setting."""
    with open(SETTINGS_FILE, encoding="utf-8") as setfile:
        settings = yaml.safe_load(setfile)
        for setting_opt in settings_path:
            settings = settings[setting_opt]
        return settings


# def get_mountables() -> Set[str]:
#     """Get a list of mountable drives."""
#     with open(MOUNT_LIST, encoding="utf-8") as mountfile:
#         mount_contents = mountfile.read()
#         return {mount.strip() for mount in mount_contents.split("\n")}


# def add_mountable(device_name: str) -> None:
#     """Add an allowable mountable device."""
#     if device_name not in get_mountables():
#         with open(MOUNT_LIST, mode="a", encoding="utf-8") as mountfile:
#             mountfile.write(f"{device_name}\n")
#     else:
#         print("This device name is already allowed.")
#         sys.exit(0)
