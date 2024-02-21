# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests startup functionality.

Author(s): Alec Delaney
"""

import os

import circfirm.backend
import circfirm.startup
import tests.helpers


def test_ensure_dir() -> None:
    """Tests the ensure_dir() function."""
    mount_location = tests.helpers.get_mount()
    test_dir = os.path.join(mount_location, "testdir")

    try:
        circfirm.startup.ensure_dir(test_dir)
        assert os.path.exists(test_dir)
    finally:
        os.rmdir(test_dir)


def test_ensure_file() -> None:
    """Tests the _ensure_file() function."""
    mount_location = tests.helpers.get_mount()
    test_file = os.path.join(mount_location, "testfile")
    try:
        circfirm.startup._ensure_file(test_file)
        assert os.path.exists(test_file)
    finally:
        os.remove(test_file)


def test_ensure_app_setup() -> None:
    """Tests the ensure_app_setup() function."""
    mount_location = tests.helpers.get_mount()
    testfolder = os.path.join(mount_location, "testfolder")
    testfile = os.path.join(testfolder, "testfile")
    circfirm.startup.FOLDER_LIST.append(testfolder)
    circfirm.startup.FILE_LIST.append(testfile)
    try:
        circfirm.startup.ensure_app_setup()
        assert os.path.exists(testfolder)
        assert os.path.exists(testfile)
    finally:
        os.remove(testfile)
        os.rmdir(testfolder)
