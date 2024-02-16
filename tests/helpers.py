# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Helpers for tests.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil


def get_mount() -> str:
    """Get the mounted drive."""
    mount_location = os.path.join(os.path.curdir, "testmount")
    assert os.path.exists(mount_location)
    assert os.path.isdir(mount_location)
    return os.path.realpath(mount_location)


def get_mount_node(path: str, must_exist: bool = False) -> str:
    """Get a file or folder on the mounted drive."""
    mount_location = get_mount()
    node_location = os.path.join(mount_location, path)
    if must_exist:
        assert os.path.exists(node_location)
    return node_location

def touch_mount_node(path: str, exist_ok: bool = False) -> str:
    """Touch a file on the mounted drive."""
    node_location = get_mount_node(path)
    pathlib.Path(node_location).touch(exist_ok=exist_ok)
    return node_location


def copy_uf2_info() -> None:
    """Copy a bootloader file to the mounted test drive."""
    template_bootloader = os.path.join("tests", "assets", "info_uf2.txt")
    bootloader_dest = os.path.join("testmount", "info_uf2.txt")
    shutil.copyfile(template_bootloader, bootloader_dest)