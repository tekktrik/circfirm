# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import sys
import shutil

import click

import circfirm
import circfirm.startup
import circfirm.backend


@click.group()
def cli() -> None:
    """Main entry point"""
    circfirm.startup.ensure_app_setup()


@cli.command()
@click.argument("version")
def install(version: str) -> None:
    """Install the specified version of CircuitPython"""
    mount_path = circfirm.backend.find_bootloader()
    if not mount_path:
        print("CircuitPython device not found!")
        print("Check that the device is connected and mounted.")
        sys.exit(1)

    board = circfirm.backend.get_board_name(mount_path)

    if not circfirm.backend.is_downloaded(board, version):
        print("Downloading UF2...")
        circfirm.backend.download_uf2(board, version)

    uf2file = circfirm.backend.get_uf2_path(board, version)
    shutil.copy(uf2file, mount_path)
    print("UF2 file copied to device!")
    print("Device should reboot momentarily.")


if __name__ == "__main__":
    cli()
