# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Shared functionality for the tool.

Author(s): Alec Delaney
"""

import click

from circfirm.startup import setup_file, setup_folder

# Folders
APP_DIR = click.get_app_dir("circfirm")
UF2_ARCHIVE = setup_folder(APP_DIR, "archive")

# Files
SETTINGS_FILE = setup_file(APP_DIR, "settings.yaml")

UF2INFO_FILE = "info_uf2.txt"
BOOTOUT_FILE = "boot_out.txt"
