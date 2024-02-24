# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Main CLI functionality for the tool.

Author(s): Alec Delaney
"""

import importlib
import os
import pkgutil
import shutil
import sys
import time
from typing import Any, Callable, Dict, Iterable, Optional

import click

import circfirm
import circfirm.backend
import circfirm.startup


@click.group()
@click.version_option(package_name="circfirm")
def cli() -> None:
    """Install CircuitPython firmware from the command line."""
    circfirm.startup.ensure_app_setup()


def announce_and_await(
    msg: str,
    func: Callable,
    args: Iterable = (),
    kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Announce an action to be performed, do it, then announce its completion."""
    if kwargs is None:
        kwargs = {}
    fmt_msg = f"{msg}..."
    click.echo(fmt_msg, nl=False)
    resp = func(*args, **kwargs)
    click.echo(" done")
    return resp


@cli.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option("-b", "--board", default=None, help="Assume the given board name")
def install(version: str, language: str, board: Optional[str]) -> None:
    """Install the specified version of CircuitPython."""
    circuitpy = circfirm.backend.find_circuitpy()
    bootloader = circfirm.backend.find_bootloader()
    if not circuitpy and not bootloader:
        click.echo("CircuitPython device not found!")
        click.echo("Check that the device is connected and mounted.")
        sys.exit(1)

    if not board:
        if not circuitpy and bootloader:
            click.echo("CircuitPython device found, but it is in bootloader mode!")
            click.echo(
                "Please put the device out of bootloader mode, or use the --board option."
            )
            sys.exit(3)
        board = circfirm.backend.get_board_name(circuitpy)

        click.echo("Board name detected, please switch the device to bootloader mode.")
        while not (bootloader := circfirm.backend.find_bootloader()):
            time.sleep(1)

    if not bootloader:
        if circfirm.backend.find_circuitpy():
            click.echo("CircuitPython device found, but is not in bootloader mode!")
            click.echo("Please put the device in bootloader mode.")
            sys.exit(2)

    if not circfirm.backend.is_downloaded(board, version, language):
        try:
            announce_and_await(
                "Downloading UF2",
                circfirm.backend.download_uf2,
                args=(board, version, language),
            )
        except ConnectionError as err:
            click.echo(" failed")  # Mark as failed
            click.echo(f"Error: {err.args[0]}")
            sys.exit(4)
    else:
        click.echo("Using cached firmware file")

    uf2file = circfirm.backend.get_uf2_filepath(board, version, language)
    uf2filename = os.path.basename(uf2file)
    uf2_path = os.path.join(bootloader, uf2filename)
    announce_and_await(
        f"Copying UF2 to {board}", shutil.copyfile, args=(uf2file, uf2_path)
    )
    click.echo("Device should reboot momentarily.")


cli_pkg_path = os.path.join("circfirm", "cli")
plugin_names = [modname for _, modname, _ in pkgutil.iter_modules((cli_pkg_path,))]

for plugin_name in plugin_names:
    import_name = ".".join(["circfirm", "cli", plugin_name])
    module = importlib.import_module(import_name)
    source_cli: click.MultiCommand = getattr(module, "cli")
    plugin = click.CommandCollection(sources=(source_cli,))
    plugin.help = source_cli.__doc__
    cli.add_command(plugin, plugin_name)
