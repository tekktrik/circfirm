# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Basic startup functionality for the tools.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
from typing import List, Tuple

import click

FOLDER_LIST: List[str] = []
FILE_LIST: List[str] = []
TEMPLATE_LIST: List[Tuple[str, str]] = []


def specify_app_dir(app_name: str) -> str:
    """Set up the application directory."""
    app_path = click.get_app_dir(app_name)
    FOLDER_LIST.append(app_path)
    return app_path


def specify_folder(*path_parts: str) -> str:
    """Add a folder to the global record list."""
    folder_path = os.path.join(*path_parts)
    FOLDER_LIST.append(folder_path)
    return folder_path


def specify_file(*path_parts: str) -> str:
    """Add a file to the global record list."""
    file_path = os.path.join(*path_parts)
    FILE_LIST.append(file_path)
    return file_path


def specify_template(src_path: str, dest_path: str) -> str:
    """Add a template to the global record list."""
    TEMPLATE_LIST.append((src_path, dest_path))
    return dest_path


def ensure_dir(dir_path: str, /) -> None:
    """Ensure the directory exists, create if needed."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def _ensure_file(file_path: str, /) -> None:
    """Ensure the file exists, touch to create if needed."""
    if not os.path.exists(file_path):
        pathlib.Path(file_path).touch(exist_ok=True)


def ensure_template(src_path: str, dest_path: str, /) -> None:
    """Ensure the template exists, copy it if needed."""
    if not os.path.exists(dest_path):
        shutil.copyfile(src_path, dest_path)


def ensure_app_setup() -> None:
    """Ensure the entire application folder is set up."""
    for folder in FOLDER_LIST:
        ensure_dir(folder)
    for file in FILE_LIST:
        _ensure_file(file)
    for template in TEMPLATE_LIST:
        ensure_template(*template)
