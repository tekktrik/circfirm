# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Helpers for tests.

Author(s): Alec Delaney
"""

import os
import pathlib
import platform
import shutil
import threading
import time

import circfirm


def start_bootloader_copy_thread() -> None:
    """Wait then add the boot_out.txt file."""

    def wait_and_set_bootloader() -> None:
        time.sleep(2)
        delete_mount_node(circfirm.BOOTOUT_FILE)
        copy_uf2_info()

    threading.Thread(target=wait_and_set_bootloader).start()


def set_firmware_version(version: str) -> None:
    """Artificially set the recorded firmware version."""
    bootloader_path = os.path.join(get_mount(), circfirm.BOOTOUT_FILE)

    with open(bootloader_path, encoding="utf-8") as bootfile:
        contents = bootfile.read()

    new_contents = contents.replace("8.0.0-beta.6", version)

    with open(bootloader_path, mode="w", encoding="utf-8") as bootfile:
        bootfile.write(new_contents)


def get_mount() -> str:
    """Get the mounted drive."""
    if platform.system() == "Windows":  # pragma: no cover
        mount_location = "T:\\"
    elif platform.system() == "Darwin":  # pragma: no cover
        mount_location = "/Volumes/TESTMOUNT"
    else:  # pragma: no cover
        mount_location = os.path.join(os.path.curdir, "testmount")
    assert os.path.exists(mount_location)
    assert os.path.isdir(mount_location)
    return (
        mount_location
        if platform.system() == "Windows"
        else os.path.realpath(mount_location)
    )


def get_mount_node(path: str) -> str:
    """Get a file or folder on the mounted drive."""
    mount_location = get_mount()
    return os.path.join(mount_location, path)


def delete_mount_node(path: str, missing_ok: bool = False) -> None:
    """Delete a file on the mounted druve."""
    node_file = get_mount_node(path)
    pathlib.Path(node_file).unlink(missing_ok=missing_ok)


def _copy_text_file(filename: str) -> None:
    """Copy a text file to the mounted test drive."""
    template_bootloader = os.path.join("tests", "assets", filename)
    bootloader_dest = os.path.join(get_mount(), filename)
    shutil.copyfile(template_bootloader, bootloader_dest)


def copy_uf2_info() -> None:
    """Copy a bootloader file to the mounted test drive."""
    _copy_text_file("info_uf2.txt")


def copy_boot_out() -> None:
    """Copy a bootout file to the mounted test drive."""
    _copy_text_file("boot_out.txt")


def get_board_ids_from_git() -> list[str]:
    """Get a list of board IDs from the sandbox git repository."""
    ports_path = pathlib.Path("tests/sandbox/circuitpython")
    board_paths = ports_path.glob("ports/*/boards/*")
    return sorted(
        [board_path.name for board_path in board_paths if board_path.is_dir()]
    )
