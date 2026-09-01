# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
# SPDX-License-Identifier: MIT

"""CLI functionality for the update subcommand.

Author(s): Alec Delaney
"""

import sys

import botocore.exceptions
import click
import packaging.version

import circfirm.backend.device
import circfirm.backend.s3


@click.command()
@click.option(
    "-b",
    "--board-id",
    default=None,
    help="Assume the given board ID (and connect in bootloader mode)",
)
@click.option("-l", "--language", default="en_US", help="CircuitPython langauge/locale")
@click.option(
    "-t",
    "--timeout",
    default=-1,
    help="Set a timeout in seconds for the switch to bootloader mode",
)
@click.option(
    "-p",
    "--pre-release",
    is_flag=True,
    default=False,
    help="Whether pre-release versions should be considered",
)
@click.option(
    "-y",
    "--limit-to-minor",
    is_flag=True,
    default=False,
    help="Upgrade up to minor version updates",
)
@click.option(
    "-z",
    "--limit-to-patch",
    is_flag=True,
    default=False,
    help="Upgrade up to patch version updates",
)
def cli(  # noqa: PLR0913
    board_id: str | None,
    language: str,
    timeout: int,
    pre_release: bool,
    limit_to_minor: bool,
    limit_to_patch: bool,
) -> None:
    """Update a connected board to the latest CircuitPython version."""
    circuitpys, bootloaders = circfirm.cli.get_connection_statuses()

    if not circuitpys and not board_id:
        click.echo("CircuitPython devices found, but all are in bootloader mode!")
        circfirm.cli.warn_not_circuitpy_mode()

    device_path = circfirm.cli.get_device_from_all_connected(circuitpys, bootloaders)

    if device_path in circuitpys:
        board_id, current_version = (
            circfirm.backend.device.get_board_info_from_circuitpy(device_path)
        )
        try:
            bootloader = circfirm.cli.ensure_bootloader_mode(
                device_path, timeout=timeout
            )
        except OSError as err:
            raise click.ClickException(err.args[0])
    elif not board_id:
        circfirm.cli.warn_not_circuitpy_mode()
    else:
        click.echo(
            "Bootloader mode detected - cannot check the currently installed version"
        )
        click.echo(
            "The latest version will be installed regardless of the currently installed version."
        )
        current_version = "0.0.0"
        bootloader = device_path

    try:
        _ = packaging.version.Version(current_version)
    except packaging.version.InvalidVersion:
        click.echo(
            f"Board currently has version {current_version}, which cannot be used for version comparison."
        )
        click.echo(
            "Please use the install command to explicitly install a specific version."
        )
        sys.exit(1)

    try:
        new_versions = circfirm.backend.s3.get_board_versions(board_id, language)
    except botocore.exceptions.ConnectionError as err:
        raise click.exceptions.ClickException(err.args[0])

    if not pre_release:
        new_versions = [
            version
            for version in new_versions
            if not packaging.version.Version(version).is_prerelease
        ]

    if limit_to_minor or limit_to_patch:
        new_versions = [
            version
            for version in new_versions
            if packaging.version.Version(version).major
            <= packaging.version.Version(current_version).major
        ]
    if limit_to_patch:
        new_versions = [
            version
            for version in new_versions
            if packaging.version.Version(version).minor
            <= packaging.version.Version(current_version).minor
        ]

    if not new_versions:
        raise click.ClickException(
            "No versions exist that meet the given update criteria"
        )

    new_version = new_versions[0]
    if packaging.version.Version(current_version) >= packaging.version.Version(
        new_version
    ):
        click.echo(
            f"Current version ({current_version}) is at or higher than proposed new update ({new_version})"
        )
        return

    circfirm.cli.download_if_needed(board_id, new_version, language)
    circfirm.cli.copy_cache_firmware(board_id, new_version, language, bootloader)
