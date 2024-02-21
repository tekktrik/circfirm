# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Pytest configuration file.

Author(s): Alec Delaney
"""

import pathlib
import shutil
from typing import Union

import click
import pytest

BACKUP_FOLDER = pathlib.Path("tests/backup/")
APP_DIR = pathlib.Path(click.get_app_dir("circfirm")).resolve()

CONFIG_EXISTS = APP_DIR.exists()


def pytest_sessionstart(session: pytest.Session) -> None:
    """Save the current cron table before testing."""
    BACKUP_FOLDER.mkdir(exist_ok=True)
    if CONFIG_EXISTS:  # pragma: no cover
        shutil.move(APP_DIR, "tests/backup")


def pytest_sessionfinish(
    session: pytest.Session, exitstatus: Union[int, pytest.ExitCode]
) -> None:
    """Restore the previous cron table after testing."""
    try:
        shutil.rmtree(APP_DIR)
    except FileNotFoundError:  # pragma: no cover
        pass
    if CONFIG_EXISTS:  # pragma: no cover
        shutil.move("tests/backup/circfirm", APP_DIR.parent)
