# SPDX-FileCopyrightText: 2022 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Pytest configuration file.

Author(s): Alec Delaney
"""

import os
import pathlib
import shutil
from collections.abc import Iterator
from typing import NoReturn, Union

import botocore.exceptions
import click
import pytest
import requests
import yaml
from botocore.httpsession import URLLib3Session

import circfirm
from tests.helpers import copy_boot_out, copy_uf2_info, delete_mount_node

BACKUP_FOLDER = pathlib.Path("tests/backup/")
APP_DIR = pathlib.Path(click.get_app_dir("circfirm")).resolve()

CONFIG_EXISTS = APP_DIR.exists()


# pytest session configuration


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
    session: pytest.Session, exitstatus: int | pytest.ExitCode
) -> None:
    """Restore the previous cron table after testing."""
    try:
        shutil.rmtree(APP_DIR)
    except FileNotFoundError:  # pragma: no cover
        pass
    if CONFIG_EXISTS:  # pragma: no cover
        shutil.move("tests/backup/circfirm", APP_DIR.parent)


# Fixtures for mocking device connections


@pytest.fixture
def mock_with_circuitpy() -> Iterator[None]:
    """Run a with a device connected in CIRCUITPY mode."""
    delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
    delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
    copy_boot_out()

    yield

    delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)


@pytest.fixture
def mock_with_bootloader() -> Iterator[None]:
    """Run with a device connected in bootloader mode."""  # noqa: D401
    delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
    delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)
    copy_uf2_info()

    yield

    delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)


@pytest.fixture
def mock_with_no_device() -> None:
    """Run without a device connected in either CIRCUITPY or bootloader mode."""  # noqa: D401
    delete_mount_node(circfirm.BOOTOUT_FILE, missing_ok=True)
    delete_mount_node(circfirm.UF2INFO_FILE, missing_ok=True)


# Fixtures for mocking cached firmwares


@pytest.fixture
def mock_with_firmwares_archived() -> Iterator[None]:
    """Run with the test firmwares in the cache archive."""  # noqa: D401
    firmware_folder = pathlib.Path("tests/assets/firmwares")
    for board_folder in firmware_folder.glob("*"):
        shutil.copytree(
            board_folder, os.path.join(circfirm.UF2_ARCHIVE, board_folder.name)
        )

    yield

    if os.path.exists(circfirm.UF2_ARCHIVE):
        shutil.rmtree(circfirm.UF2_ARCHIVE)
    os.mkdir(circfirm.UF2_ARCHIVE)


# Fixtures for mocking no internet connection


@pytest.fixture
def mock_requests_no_internet(monkeypatch: pytest.MonkeyPatch) -> NoReturn:
    """Simulate a network error by raising requests.ConnectionError."""

    def mock_get(*args, **kwargs) -> NoReturn:
        """Mock GET function."""
        raise requests.ConnectionError

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_s3_no_internet(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatch for an S3 command run without an internet connection."""

    def mock_send(self, *args, **kwargs) -> NoReturn:
        """Mock send method."""
        raise botocore.exceptions.EndpointConnectionError(endpoint_url="test")

    monkeypatch.setattr(URLLib3Session, "send", mock_send)


# Fixtures for working with GitHub tokens in settings file


@pytest.fixture
def token(request: pytest.FixtureRequest) -> Iterator[None]:
    """Perform a test with the given token in the configuration settings."""

    def get_default_token() -> str:
        """Get the default test token."""
        return os.environ["GH_TOKEN"]

    def set_token(new_token: str) -> str:
        """Set a new token."""
        with open(circfirm.SETTINGS_FILE, encoding="utf-8") as setfile:
            contents = yaml.safe_load(setfile)
            prev_token = contents["token"]["github"]
            contents["token"]["github"] = new_token
        with open(circfirm.SETTINGS_FILE, mode="w", encoding="utf-8") as setfile:
            yaml.safe_dump(contents, setfile)
        return prev_token

    token: str = getattr(request, "param", get_default_token())
    prev_token = set_token(token)
    yield
    set_token(prev_token)
