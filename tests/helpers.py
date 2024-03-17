# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Helpers for tests.

Author(s): Alec Delaney
"""

import os
import pathlib
import platform
import shutil
import time
from typing import Any, Callable, Dict, List, TypeVar

import pytest
import yaml

import circfirm
import circfirm.backend

_T = TypeVar("_T")


def as_circuitpy(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with a device connected in CIRCUITPY mode."""  # noqa: D401

    def as_circuitpy_wrapper(*args, **kwargs) -> _T:
        delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
        delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
        copy_boot_out()
        result = func(*args, **kwargs)
        delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
        return result

    return as_circuitpy_wrapper


def as_bootloader(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with a device connected in bootloader mode."""  # noqa: D401

    def as_bootloader_wrapper(*args, **kwargs) -> _T:
        delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
        delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
        copy_uf2_info()
        result = func(*args, **kwargs)
        delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
        return result

    return as_bootloader_wrapper


def as_not_present(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function without a device connected in either CIRCUITPY or bootloader mode."""  # noqa: D401

    def as_not_present_wrapper(*args, **kwargs) -> _T:
        delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
        delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
        return func(*args, **kwargs)

    return as_not_present_wrapper


def with_firmwares(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with the test firmwares in the cache archive."""  # noqa: D401

    def with_firmwares_wrapper(*args, **kwargs) -> _T:
        firmware_folder = pathlib.Path("tests/assets/firmwares")
        for board_folder in firmware_folder.glob("*"):
            shutil.copytree(
                board_folder, os.path.join(circfirm.UF2_ARCHIVE, board_folder.name)
            )

        result = func(*args, **kwargs)

        if os.path.exists(circfirm.UF2_ARCHIVE):
            shutil.rmtree(circfirm.UF2_ARCHIVE)
        os.mkdir(circfirm.UF2_ARCHIVE)

        return result

    return with_firmwares_wrapper


def wait_and_set_bootloader() -> None:
    """Wait then add the boot_out.txt file."""
    time.sleep(2)
    delete_mount_node(circfirm.BOOTOUT_FILE)
    copy_uf2_info()


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


def get_board_ids_from_git() -> List[str]:
    """Get a list of board IDs from the sandbox git repository."""
    ports_path = pathlib.Path("tests/sandbox/circuitpython")
    board_paths = ports_path.glob("ports/*/boards/*")
    return sorted(
        [board_path.name for board_path in board_paths if board_path.is_dir()]
    )


def with_token(token: str, use_monkeypatch: bool = False) -> None:
    """Perform a test with the given token in the configuration settings."""

    def set_token(new_token: str) -> str:
        """Set a new token."""
        with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
            contents = yaml.safe_load(setfile)
            prev_token = contents["token"]["github"]
            contents["token"]["github"] = new_token
        with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as setfile:
            yaml.safe_dump(contents, setfile)
        return prev_token

    def with_token_set(func: Callable) -> None:
        def with_token_set_wrapper(*args: Any, **kwargs: Dict[str, Any]) -> None:
            prev_token = set_token(token)
            func(*args, **kwargs)
            set_token(prev_token)

        def with_token_set_wrapper_monkeypatch(
            monkeypatch: pytest.MonkeyPatch, *args: Any, **kwargs: Dict[str, Any]
        ) -> None:
            prev_token = set_token(token)
            func(monkeypatch, *args, **kwargs)
            set_token(prev_token)

        if use_monkeypatch:
            return with_token_set_wrapper_monkeypatch
        return with_token_set_wrapper

    return with_token_set
