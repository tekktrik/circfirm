# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Main CLI functionality for the tool.

Author(s): Alec Delaney
"""

import os
import shutil
import sys
from typing import Dict, Optional, Set

import click

import circfirm
import circfirm.backend
import circfirm.startup

__version__ = "0.0.0+auto.0"


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Install CircuitPython firmware from the command line."""
    circfirm.startup.ensure_app_setup()


@cli.command()
@click.argument("version")
def install(version: str) -> None:
    """Install the specified version of CircuitPython."""
    mount_path = circfirm.backend.find_bootloader()
    if not mount_path:
        print("CircuitPython device not found!")
        print("Check that the device is connected and mounted.")
        sys.exit(1)

    board = circfirm.backend.get_board_name(mount_path)

    if not circfirm.backend.is_downloaded(board, version):
        print("Downloading UF2...")
        circfirm.backend.download_uf2(board, version)

    uf2file = circfirm.backend.get_uf2_filepath(board, version)
    shutil.copy(uf2file, mount_path)
    print("UF2 file copied to device!")
    print("Device should reboot momentarily.")


@cli.group()
def cache():
    """Work with cached information."""


@cache.command()
@click.option("-b", "--board", default=None)
def clear(board: Optional[str]) -> None:
    """Clear the cache, either entirely or for a specific board/version."""
    if board is None:
        shutil.rmtree(circfirm.UF2_ARCHIVE)
        circfirm.startup.ensure_app_setup()
        return
    if "=" not in board:
        version = None
    else:
        board, version = board.split("=")
    board = board.replace(" ", "_").lower()

    uf2_file = circfirm.backend.get_uf2_filepath(board, version)
    board_folder = os.path.dirname(uf2_file)

    # No UF2 files exist for the board
    if not os.path.exists(board_folder):
        print("No UF2 files downloaded for this board!")
        sys.exit(1)

    # Board cache exists, and no specific version given
    if version is None and os.path.exists(board_folder):
        shutil.rmtree(board_folder)
        print("Cache cleared!")
        sys.exit(0)

    # Specific board and version given, but do not exist
    if not os.path.exists(uf2_file):
        board_name = board.replace(" ", "_").lower()
        print(f"No UF2 downloaded for version {version} of the {board_name}!")
        sys.exit(1)

    # Specific board and version given that do exist
    os.remove(uf2_file)

    # Delete board folder if empty
    if len(os.listdir(board_folder)) == 0:
        shutil.rmtree(board_folder)


@cache.command(name="list")
@click.option("-b", "--board", default=None)
def cache_list(board: Optional[str]) -> None:
    """List all the boards/versions cached."""
    if board is not None:
        board_name = board.replace(" ", "_").lower()
    board_list = os.listdir(circfirm.UF2_ARCHIVE)

    if not board_list:
        print("Versions have not been cached yet for any boards.")
        sys.exit(0)

    if board is not None and board_name not in board_list:
        print(f"No versions for board '{board_name}' are not cached.")
        sys.exit(0)

    boards: Dict[str, Set[str]] = {}
    for board_folder in os.listdir(circfirm.UF2_ARCHIVE):
        if board is not None and board_name != board_folder:
            continue
        dummy_file = os.path.basename(
            circfirm.backend.get_uf2_filepath(board_folder, "0.0.0")
        )
        leading, _ = dummy_file.split("0.0.0")
        board_folder_full = os.path.join(circfirm.UF2_ARCHIVE, board_folder)
        versions = {ver[len(leading) : -4] for ver in os.listdir(board_folder_full)}
        boards[board_folder] = versions

    for rec_boardname, rec_boardvers in boards.items():
        print(f"{rec_boardname}")
        for rec_boardver in rec_boardvers:
            print(f"  * {rec_boardver}")


@cache.command(name="install")
@click.argument("board")
@click.argument("version")
def cache_install(board: str, version: str) -> None:
    """Install a version of CircuitPython to cache."""
    circfirm.backend.download_uf2(board, version)


if __name__ == "__main__":
    cli()
