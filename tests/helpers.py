# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Helpers for tests.

Author(s): Alec Delaney
"""

import json
import os
import pathlib
import platform
import shutil
import threading
import time

import circfirm

DELAY_TIME_S = 1


def start_bootloader_copy_thread(mount_index: int = 0) -> None:
    """Wait then add the info_uf2.txt file."""

    def wait_and_set_bootloader() -> None:
        time.sleep(DELAY_TIME_S)
        delete_mount_node(circfirm.BOOTOUT_FILE, mount_index)
        time.sleep(DELAY_TIME_S)
        copy_uf2_info(mount_index)

    threading.Thread(target=wait_and_set_bootloader).start()


def start_multiple_bootloader_copy_thread() -> None:
    """Wait then add multiple info_uf2.txt files."""

    def wait_and_set_bootloaders() -> None:
        time.sleep(DELAY_TIME_S)
        delete_mount_node(circfirm.BOOTOUT_FILE)
        time.sleep(DELAY_TIME_S)
        copy_uf2_info(1)
        copy_uf2_info(0)

    threading.Thread(target=wait_and_set_bootloaders).start()


def set_firmware_version(version: str) -> None:
    """Artificially set the recorded firmware version."""
    bootloader_path = os.path.join(get_mount(), circfirm.BOOTOUT_FILE)

    with open(bootloader_path, encoding="utf-8") as bootfile:
        contents = bootfile.read()

    new_contents = contents.replace("8.0.0-beta.6", version)

    with open(bootloader_path, mode="w", encoding="utf-8") as bootfile:
        bootfile.write(new_contents)


def get_mount(mount_index: int = 0, missing_ok: bool = False) -> str:
    """Get the mounted drive."""
    with open("scripts/info.json") as jsonfile:
        contents = json.load(jsonfile)

    try:
        system = platform.system()
    except KeyError:  # pragma: no cover
        raise RuntimeError("Unsupported OS detected")
    drivefile, directory = contents[system][mount_index]

    if platform.system() == "Windows":  # pragma: no cover
        mount_location = f"{drivefile}\\"
    elif platform.system() == "Darwin":  # pragma: no cover
        mount_location = f"/Volumes/{directory}"
    else:  # pragma: no cover
        mount_location = os.path.join(os.path.curdir, directory)

    if not missing_ok:
        assert os.path.exists(mount_location)
        assert os.path.isdir(mount_location)

    return mount_location if system == "Windows" else os.path.realpath(mount_location)


def get_mount_node(path: str, mount_index: int = 0, missing_ok: bool = False) -> str:
    """Get a file or folder on the mounted drive."""
    mount_location = get_mount(mount_index, missing_ok)
    return os.path.join(mount_location, path)


def delete_mount_node(
    path: str, mount_index: int = 0, missing_ok: bool = False
) -> None:
    """Delete a file on the mounted druve."""
    node_file = get_mount_node(path, mount_index, missing_ok=missing_ok)
    pathlib.Path(node_file).unlink(missing_ok=missing_ok)


def _copy_text_file(filename: str, mount_index: int = 0) -> None:
    """Copy a text file to the mounted test drive."""
    template_file = os.path.join("tests", "assets", filename)
    mount_dest = os.path.join(get_mount(mount_index), filename)
    shutil.copyfile(template_file, mount_dest)


def copy_uf2_info(mount_index: int = 0) -> None:
    """Copy a bootloader file to the mounted test drive."""
    _copy_text_file("info_uf2.txt", mount_index)


def copy_boot_out(mount_index: int = 0) -> None:
    """Copy a bootout file to the mounted test drive."""
    _copy_text_file("boot_out.txt", mount_index)


def get_board_ids_from_git() -> list[str]:
    """Get a list of board IDs from the sandbox git repository."""
    ports_path = pathlib.Path("tests/sandbox/circuitpython")

    # Glob both Zephyr and non-Zephyr boards
    nonzephyr_board_paths = ports_path.glob("ports/*/boards/*")
    zephyr_board_paths = ports_path.glob("ports/zephyr-cp/boards/*/*")

    # Remove Zephyr boards from the non-Zephyr list
    nonzephyr_board_paths = [
        board_path.name
        for board_path in nonzephyr_board_paths
        if "zephyr-cp" not in board_path.parts and board_path.is_dir()
    ]

    # Clean up the Zephyr boards
    zephyr_board_paths = [
        board_path.parent.name + "_" + board_path.name
        for board_path in zephyr_board_paths
        if board_path.is_dir()
    ]

    return sorted(nonzephyr_board_paths + zephyr_board_paths)


def copy_default_config() -> str:
    """Copy the default configuration settings."""
    with open(circfirm.SETTINGS_FILE) as settings_file:
        contents = settings_file.read()
    shutil.copyfile("circfirm/templates/settings.yaml", circfirm.SETTINGS_FILE)
    return contents
