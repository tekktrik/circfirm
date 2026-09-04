# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the devices subcommand.

Author(s): Alec Delaney
"""

import click

import circfirm.backend.device


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Detect connected CircuitPython boards."""
    if ctx.invoked_subcommand is None:
        circuitpys = circfirm.backend.device.find_circuitpys()
        bootloaders = circfirm.backend.device.find_bootloaders()

        devices = circuitpys + bootloaders
        are_circuitpys = [device in circuitpys for device in devices]

        if not devices:
            click.echo("No boards connected in either CIRCUITPY or bootloader modes")
            return

        for device_path, is_circuitpy in sorted(
            zip(devices, are_circuitpys, strict=True)
        ):
            if is_circuitpy:
                name, version = circfirm.backend.device.get_board_info_from_circuitpy(
                    device_path
                )
                formatted = circfirm.cli.format_circuitpy_info(
                    device_path, name, version, "[CIRCUITPY]"
                )
            else:
                formatted = circfirm.cli.format_bootloader_info(
                    device_path, "[bootloader]"
                )
            click.echo(formatted)


@cli.command(name="circuitpy")
@click.option(
    "-p",
    "--paths-only",
    is_flag=True,
    default=False,
    help="Return only paths",
)
def devices_circuitpy(paths_only: bool) -> None:
    """Detect connected boards in CIRCUITPY or equivalent mode."""
    circuitpys = circfirm.backend.device.find_circuitpys()

    if not circuitpys:
        click.echo("No board connected in CIRCUITPY or equivalent mode")
        return

    for device_path in sorted(circuitpys):
        name, version = circfirm.backend.device.get_board_info_from_circuitpy(
            device_path
        )
        formatted = (
            circfirm.cli.format_circuitpy_info(device_path, name, version)
            if not paths_only
            else device_path
        )
        click.echo(formatted)


@cli.command(name="bootloader")
def devices_bootloader() -> None:
    """Detect connected boards in bootloader mode."""
    bootloaders = circfirm.backend.device.find_bootloaders()

    if not bootloaders:
        click.echo("No board connected in bootloader mode")
        return

    for device_path in sorted(bootloaders):
        formatted = circfirm.cli.format_bootloader_info(device_path)
        click.echo(formatted)
