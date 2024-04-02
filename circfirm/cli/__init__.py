# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Main CLI functionality for the tool.

Author(s): Alec Delaney
"""

import importlib.util
import os
import pkgutil
import shutil
import sys
import time
import types
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar

import click
import click_spinner

import circfirm
import circfirm.backend.cache
import circfirm.backend.config
import circfirm.backend.device
import circfirm.startup

_T = TypeVar("_T")


@click.group(name="circfirm")
@click.version_option(package_name="circfirm")
def cli() -> None:
    """Manage CircuitPython firmware from the command line."""


def _maybe_output(msg: str, setting_path: Iterable[str], invert: bool = False) -> None:
    """Output text based on the configurable settings."""
    settings = get_settings()
    for path in setting_path:
        settings = settings[path]
    settings = not settings if invert else settings
    if settings:
        click.echo(msg)


def maybe_support(msg: str) -> None:
    """Output supporting text based on the configurable settings."""
    _maybe_output(msg, ("output", "supporting", "silence"), invert=True)


def maybe_warn(msg: str) -> None:
    """Output warning text based on the configurable settings."""
    _maybe_output(msg, ("output", "warning", "silence"), invert=True)


def get_board_id(
    circuitpy: Optional[str],
    bootloader: Optional[str],
    board: Optional[str],
    timeout: int = -1,
) -> Tuple[str, str]:
    """Get the board ID of a device via CLI."""
    if not board:
        if not circuitpy and bootloader:
            click.echo("CircuitPython device found, but it is in bootloader mode!")
            click.echo(
                "Please put the device out of bootloader mode, or use the --board-id option."
            )
            sys.exit(3)
        board = circfirm.backend.device.get_board_info(circuitpy)[0]

        click.echo("Board ID detected, please switch the device to bootloader mode.")
        if timeout == -1:
            skip_timeout = True
        else:
            skip_timeout = False
            start_time = time.time()

        while not (bootloader := circfirm.backend.device.find_bootloader()):
            if not skip_timeout and time.time() >= start_time + timeout:
                raise OSError(
                    "Bootloader mode device not found within the timeout period"
                )
            time.sleep(0.05)
    return bootloader, board


def get_connection_status() -> Tuple[Optional[str], Optional[str]]:
    """Get the status of a connectted CircuitPython device as a CIRCUITPY and bootloader location."""
    circuitpy = circfirm.backend.device.find_circuitpy()
    bootloader = circfirm.backend.device.find_bootloader()
    if not circuitpy and not bootloader:
        click.echo("CircuitPython device not found!")
        click.echo("Check that the device is connected and mounted.")
        sys.exit(1)
    return circuitpy, bootloader


def ensure_bootloader_mode(bootloader: Optional[str]) -> None:
    """Ensure the connected device is in bootloader mode."""
    if not bootloader:
        if circfirm.backend.device.find_circuitpy():
            click.echo("CircuitPython device found, but is not in bootloader mode!")
            click.echo("Please put the device in bootloader mode.")
            sys.exit(2)


def download_if_needed(board: str, version: str, language: str) -> None:
    """Download the firmware for a given board, version, and language via CLI."""
    if not circfirm.backend.cache.is_downloaded(board, version, language):
        try:
            announce_and_await(
                "Downloading UF2",
                circfirm.backend.cache.download_uf2,
                args=(board, version, language),
            )
        except ConnectionError as err:
            click.echo(" failed")  # Mark as failed
            click.echo(f"Error: {err.args[0]}")
            sys.exit(4)
    else:
        click.echo("Using cached firmware file")


def copy_cache_firmware(
    board: str, version: str, language: str, bootloader: str
) -> None:
    """Copy the cached firmware for a given board, version, and language to the bootloader via CLI."""
    uf2file = circfirm.backend.cache.get_uf2_filepath(board, version, language)
    uf2filename = os.path.basename(uf2file)
    uf2_path = os.path.join(bootloader, uf2filename)
    announce_and_await(
        f"Copying UF2 to {board}", shutil.copyfile, args=(uf2file, uf2_path)
    )
    click.echo(f"CircuitPython version now upgraded to {version}")
    click.echo("Device should reboot momentarily")


def announce_and_await(
    msg: str,
    func: Callable[..., _T],
    args: Iterable = (),
    kwargs: Optional[Dict[str, Any]] = None,
    *,
    use_spinner: bool = True,
) -> _T:
    """Announce an action to be performed, do it, then announce its completion."""
    if kwargs is None:
        kwargs = {}
    fmt_msg = f"{msg}..."
    spinner = click_spinner.spinner()
    click.echo(fmt_msg, nl=False)
    if use_spinner:
        spinner.start()
    try:
        try:
            resp = func(*args, **kwargs)
        finally:
            if use_spinner:
                spinner.stop()
        click.echo(" done")
        return resp
    except BaseException as err:
        click.echo(" failed")
        raise err


def get_settings() -> Dict[str, Any]:
    """Get the contents of the settings file."""
    return circfirm.backend.config.get_config_settings(circfirm.SETTINGS_FILE)


def load_subcmd_folder(
    path: str,
    super_import_name: Optional[str] = None,
    *,
    filenames_as_commands: bool = False,
    ignore_missing_cli: bool = True,
) -> None:
    """Load subcommands dynamically from a folder of modules and packages."""
    subcmd_modtuples = [
        (modname, ispkg) for _, modname, ispkg in pkgutil.iter_modules((path,))
    ]
    subcmd_filepaths = [
        os.path.abspath(os.path.join(path, subcmd_name[0]))
        for subcmd_name in subcmd_modtuples
    ]

    for (_, ispkg), subcmd_path in zip(subcmd_modtuples, subcmd_filepaths):
        load_subcmd_file(
            subcmd_path,
            super_import_name,
            ispkg,
            filename_as_command=filenames_as_commands,
            ignore_missing_cli=ignore_missing_cli,
        )


def load_subcmd_file(
    path: str,
    super_import_name: Optional[str] = None,
    ispkg: bool = False,
    *,
    filename_as_command: bool = False,
    ignore_missing_cli: bool = True,
) -> None:
    """Load subcommands dynamically from a file."""
    modname = os.path.splitext(os.path.basename(path))[0]
    import_name = f"{super_import_name}.{modname}" if super_import_name else modname
    if ispkg:
        import_path = os.path.join(path, "__init__.py")
        search_paths = {"submodule_search_locations": []}
    else:
        import_path = path + ".py"
        search_paths = {}
    module_spec = importlib.util.spec_from_file_location(
        import_name, import_path, **search_paths
    )
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[import_name] = module
    module_spec.loader.exec_module(module)
    cmdname = modname if filename_as_command else None
    load_cmd_from_module(module, cmdname, ignore_missing_entry=ignore_missing_cli)


def load_cmd_from_module(
    module: types.ModuleType,
    cmdname: Optional[str] = None,
    *,
    ignore_missing_entry: bool = True,
):
    """Load the sub-command `cli` from the module."""
    try:
        source_cli: click.MultiCommand = getattr(module, "cli")
        if not cmdname:
            cmdname = source_cli.name
        cli.add_command(source_cli, cmdname)
    except AttributeError:
        if not ignore_missing_entry:
            raise RuntimeError("Module does not define a function named `cli()`")


# Ensure the application is set up
circfirm.startup.ensure_app_setup()


# Load extra commands from the rest of the circfirm.cli subpackage
cli_pkg_path = os.path.dirname(os.path.abspath(__file__))
cli_pkg_name = "circfirm.cli"
load_subcmd_folder(
    cli_pkg_path,
    super_import_name=cli_pkg_name,
    filenames_as_commands=True,
    ignore_missing_cli=False,
)

# Load downloaded plugins
settings = get_settings()
downloaded_modules: List[str] = settings["plugins"]["downloaded"]
for downloaded_module in downloaded_modules:
    try:
        module = importlib.import_module(downloaded_module)
    except ModuleNotFoundError:
        maybe_warn(f"Could not load plugin {downloaded_module}, skipping")
        continue
    load_cmd_from_module(module, None)

# Load local plugins
load_subcmd_folder(circfirm.LOCAL_PLUGINS)
