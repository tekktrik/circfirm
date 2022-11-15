# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Basic startup functionality for the tools.

Author(s): Alec Delaney
"""

import os
import pathlib

import click

FOLDER_LIST = []
FILE_LIST = []


def folder(*paths) -> str:
    """Add a folder to the global record list."""
    folder_path = (
        click.get_app_dir("circfirm")
        if len(paths) == 1
        else os.path.join(paths[0], *paths[1:])
    )
    FOLDER_LIST.append(folder_path)
    return folder_path


def file(*paths) -> str:
    """Add a file to the global record list."""
    file_path = os.path.join(*paths)
    FILE_LIST.append(file_path)
    return file_path


def ensure_dir(dir_path: str, /) -> None:
    """Ensure the directory exists, create if needed."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def _ensure_file(file_path: str, /) -> None:
    """Ensure the file exists, touch to create if needed."""
    if not os.path.exists(file_path):
        pathlib.Path(file_path).touch(exist_ok=True)


def ensure_app_setup() -> None:
    """Ensure the entire application folder is set up."""
    for fol in FOLDER_LIST:
        ensure_dir(fol)
    for fil in FILE_LIST:
        _ensure_file(fil)
