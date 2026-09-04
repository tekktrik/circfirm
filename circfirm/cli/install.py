# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the install subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device
import circfirm.cli


@click.command()
@click.argument("version")
@click.option("-l", "--language", default="en_US", help="CircuitPython language/locale")
@click.option(
    "-b",
    "--board-id",
    default=None,
    help="Assume the given board ID (and connect in bootloader mode)",
)
@click.option(
    "-t",
    "--timeout",
    default=-1,
    help="Set a timeout in seconds for the switch to bootloader mode",
)
def cli(version: str, language: str, board_id: str | None, timeout: int) -> None:
    """Install the specified version of CircuitPython."""
    circuitpys, bootloaders = circfirm.cli.get_connection_statuses()

    if not circuitpys and not board_id:
        click.echo("CircuitPython devices found, but all are in bootloader mode!")
        circfirm.cli.warn_not_circuitpy_mode()

    device_path = circfirm.cli.get_device_from_all_connected(circuitpys, bootloaders)

    if device_path in circuitpys:
        board_id = (
            circfirm.backend.device.get_board_info_from_circuitpy(device_path)[0]
            if not board_id
            else board_id
        )
        try:
            bootloader = circfirm.cli.ensure_bootloader_mode(
                device_path, timeout=timeout
            )
        except OSError as err:
            raise click.ClickException(err.args[0]) from None
    elif not board_id:
        circfirm.cli.warn_not_circuitpy_mode()
    else:
        bootloader = device_path
    circfirm.cli.download_if_needed(board_id, version, language)
    circfirm.cli.copy_cache_firmware(board_id, version, language, bootloader)
