# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Main CLI functionality for the tool.

Author(s): Alec Delaney
"""

import importlib.util
import os
import pkgutil
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar

import click
import click_spinner
import yaml

import circfirm
import circfirm.backend
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
