# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Shared functionality for the tool.

Author(s): Alec Delaney
"""

import os

from circfirm.startup import (
    specify_app_dir,
    specify_file,
    specify_folder,
    specify_template,
)

# Folders
APP_DIR = specify_app_dir("circfirm")
UF2_ARCHIVE = specify_folder(APP_DIR, "archive")
PLUGINS = specify_folder(APP_DIR, "plugins")

# Files
_TEMPLATES_FOLDER = os.path.abspath(os.path.join(__file__, "..", "templates"))
_SETTINGS_FILE_SRC = os.path.join(_TEMPLATES_FOLDER, "settings.yaml")
SETTINGS_FILE = specify_template(
    _SETTINGS_FILE_SRC, os.path.join(APP_DIR, "settings.yaml")
)

UF2INFO_FILE = "info_uf2.txt"
BOOTOUT_FILE = "boot_out.txt"
