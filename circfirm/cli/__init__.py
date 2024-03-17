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
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, TypeVar

import click
import click_spinner
import yaml

import circfirm
import circfirm.backend.cache
import circfirm.backend.device
import circfirm.startup

_T = TypeVar("_T")


@click.group()
@click.version_option(package_name="circfirm")
def cli() -> None:
    """Manage CircuitPython firmware from the command line."""
    circfirm.startup.ensure_app_setup()


def maybe_support(msg: str) -> None:
    """Output supporting text based on the configurable settings."""
    settings = get_settings()
    do_output: bool = not settings["output"]["supporting"]["silence"]
    if do_output:
        click.echo(msg)


def get_board_id(
    circuitpy: Optional[str], bootloader: Optional[str], board: Optional[str]
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
        while not (bootloader := circfirm.backend.device.find_bootloader()):
            time.sleep(1)
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
    with open(circfirm.SETTINGS_FILE, encoding="utf-8") as yamlfile:
        return yaml.safe_load(yamlfile)


def load_subcmd_folder(path: str, super_import_name: str) -> None:
    """Load subcommands dynamically from a folder of modules and packages."""
    subcmd_names = [
        (modname, ispkg) for _, modname, ispkg in pkgutil.iter_modules((path,))
    ]
    subcmd_paths = [
        os.path.abspath(os.path.join(path, subcmd_name[0]))
        for subcmd_name in subcmd_names
    ]

    for (subcmd_name, ispkg), subcmd_path in zip(subcmd_names, subcmd_paths):
        import_name = ".".join([super_import_name, subcmd_name])
        import_path = subcmd_path if ispkg else subcmd_path + ".py"
        module_spec = importlib.util.spec_from_file_location(import_name, import_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        source_cli: click.MultiCommand = getattr(module, "cli")
        if isinstance(source_cli, click.Group):
            subcmd = click.CommandCollection(sources=(source_cli,))
            subcmd.help = source_cli.__doc__
        else:
            subcmd = source_cli
        cli.add_command(subcmd, subcmd_name)


# Load extra commands from the rest of the circfirm.cli subpackage
cli_pkg_path = os.path.dirname(os.path.abspath(__file__))
cli_pkg_name = "circfirm.cli"
load_subcmd_folder(cli_pkg_path, cli_pkg_name)
