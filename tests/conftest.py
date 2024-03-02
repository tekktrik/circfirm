# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Pytest configuration file.

Author(s): Alec Delaney
"""

import os
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
    # Load environment variables if not in GitHub Actions
    if "GH_TOKEN" not in os.environ:  # pragma: no cover
        with open(".env", encoding="utf-8") as envfile:
            env_contents = envfile.read()
            for envline in env_contents.split("\n"):
                if not envline:
                    continue
                name, value = envline.split("=")
                os.environ[name] = value

    # Create the backup directory
    BACKUP_FOLDER.mkdir(exist_ok=True)

    # Save existing settings, if they exist
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
