# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Helpers for tests.

Author(s): Alec Delaney
"""

import functools
import importlib
import os
import pathlib
import platform
import shutil
import time
from collections.abc import Iterable
from typing import Any, Callable, TypeVar

import pytest
import yaml

import circfirm
import circfirm.backend
import circfirm.cli

_T = TypeVar("_T")

BASE_RESPONSE = """\
Usage: circfirm [OPTIONS] COMMAND [ARGS]...

  Manage CircuitPython firmware from the command line.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:\
"""

BASE_COMMANDS = """\
  about    Information about circfirm.
  cache    Work with cached firmwares.
  config   View and update the configuration settings for the circfirm CLI.
  current  Check the information about the currently connected board.
  detect   Detect connected CircuitPython boards.
  install  Install the specified version of CircuitPython.
  query    Query things like latest versions and board lists.
  update   Update a connected board to the latest CircuitPython version.\
"""

LOCAL_COMMANDS = {
    "module_plugin.py": ("modp", "Utilize a local module plugin that will be loaded."),
    "package_plugin": ("packp", "Utilize a local package plugin that will be loaded."),
}
DOWNLOADED_COMMANDS = {
    "circfirm_hello_world": ("hello", "Say hi."),
}


def as_circuitpy(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with a device connected in CIRCUITPY mode."""  # noqa: D401

    @functools.wraps(func)
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

    @functools.wraps(func)
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

    @functools.wraps(func)
    def as_not_present_wrapper(*args, **kwargs) -> _T:
        delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
        delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
        return func(*args, **kwargs)

    return as_not_present_wrapper


def with_firmwares(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with the test firmwares in the cache archive."""  # noqa: D401

    @functools.wraps(func)
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


def with_mock_config_settings(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator for running a function with the test configuration settings."""  # noqa: D401s

    @functools.wraps(func)
    def with_config_settings_wrapper(*args, **kwargs) -> _T:
        made_dir = False
        if not os.path.exists(circfirm.APP_DIR):  # pragma: no cover
            made_dir = True
            os.mkdir(circfirm.APP_DIR)
        filepath = circfirm.SETTINGS_FILE
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as setfile:
                contents = setfile.read()
                replaced = True
        else:  # pragma: no cover
            contents = ""
            replaced = False
        filename = os.path.basename(filepath)
        test_filepath = os.path.join("tests", "assets", "settings", filename)
        shutil.copyfile(test_filepath, filepath)

        try:
            return func(*args, **kwargs)
        finally:
            if replaced:
                with open(filepath, mode="w", encoding="utf-8") as setfile:
                    setfile.write(contents)
            else:  # pragma: no cover
                os.remove(filepath)

            if made_dir:  # pragma: no cover
                shutil.rmtree(circfirm.APP_DIR)

    return with_config_settings_wrapper


def with_local_plugins(
    local_plugin_files: Iterable[str],
) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    """Decorator for running a function with the specific local plugins."""  # noqa: D401s

    def with_local_plugins_func(func: Callable[..., _T]) -> Callable[..., _T]:
        @functools.wraps(func)
        def with_local_plugins_wrapper(*args, **kwargs) -> _T:
            try:
                for local_plugin_file in local_plugin_files:
                    filepath = os.path.join("tests/assets/plugins", local_plugin_file)
                    new_filepath = os.path.join(
                        circfirm.LOCAL_PLUGINS, local_plugin_file
                    )
                    path = pathlib.Path(filepath)
                    if path.is_file():
                        shutil.copy2(filepath, new_filepath)
                    else:
                        shutil.copytree(filepath, new_filepath)
                importlib.reload(circfirm.cli)
                return func(*args, **kwargs)
            finally:
                plugins = pathlib.Path(circfirm.LOCAL_PLUGINS).glob("*")
                for plugin in plugins:
                    if plugin.is_file():
                        plugin.unlink()
                    else:
                        shutil.rmtree(plugin)
                importlib.reload(circfirm.cli)

        return with_local_plugins_wrapper

    return with_local_plugins_func


def with_downloaded_plugins(
    downloaded_plugins: Iterable[str],
) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    """Decorator for running a function with the specific downloaded plugins."""  # noqa: D401s

    def with_downloaded_plugins_func(func: Callable[..., _T]) -> Callable[..., _T]:
        @functools.wraps(func)
        def with_downloaded_plugins_wrapper(*args, **kwargs) -> _T:
            try:
                with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
                    settings = yaml.safe_load(setfile)
                settings["plugins"]["downloaded"] = downloaded_plugins
                with open(
                    circfirm.SETTINGS_FILE, mode="w", encoding="utf-8"
                ) as setfile:
                    yaml.safe_dump(settings, setfile)
                importlib.reload(circfirm.cli)
                return func(*args, **kwargs)
            finally:
                settings["plugins"]["downloaded"] = []
                with open(
                    circfirm.SETTINGS_FILE, mode="w", encoding="utf-8"
                ) as setfile:
                    yaml.safe_dump(settings, setfile)
                importlib.reload(circfirm.cli)

        return with_downloaded_plugins_wrapper

    return with_downloaded_plugins_func


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


def get_board_ids_from_git() -> list[str]:
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
        def with_token_set_wrapper(*args: Any, **kwargs: dict[str, Any]) -> None:
            prev_token = set_token(token)
            func(*args, **kwargs)
            set_token(prev_token)

        def with_token_set_wrapper_monkeypatch(
            monkeypatch: pytest.MonkeyPatch, *args: Any, **kwargs: dict[str, Any]
        ) -> None:
            prev_token = set_token(token)
            func(monkeypatch, *args, **kwargs)
            set_token(prev_token)

        if use_monkeypatch:
            return with_token_set_wrapper_monkeypatch
        return with_token_set_wrapper

    return with_token_set


def add_command_help_text(
    orig_command_text: str, new_command: str, new_help_text: str
) -> str:
    """Add new help text for a give command."""
    commands = orig_command_text.split("\n")
    new_command_text = f"  {new_command}".ljust(11) + new_help_text
    commands.append(new_command_text)
    sorted_commands = sorted(commands, key=lambda x: x[2:5])
    return "\n".join(sorted_commands)


def get_help_response(
    local_plugin_files: Iterable[str] = (), downloaded_plugins: Iterable[str] = ()
) -> str:
    """Get the help response with specific plugins."""
    base_help_text = BASE_COMMANDS
    plugin_pairs = zip(
        (local_plugin_files, downloaded_plugins), (LOCAL_COMMANDS, DOWNLOADED_COMMANDS)
    )
    for plugins, entry_source in plugin_pairs:
        for plugin in plugins:
            cmdname, cmddesc = entry_source[plugin]
            base_help_text = add_command_help_text(
                base_help_text.rstrip(), cmdname, cmddesc
            )
    return "\n".join((BASE_RESPONSE, base_help_text.rstrip())) + "\n"
