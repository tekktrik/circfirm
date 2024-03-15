# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend GitHub functionality.

Author(s): Alec Delaney
"""

from collections import namedtuple
from functools import partial
from typing import List

import boto3.resources.collection
import pytest

import circfirm.backend.s3

MockS3Object = namedtuple("MockS3Object", ["key"])


def get_fake_s3_objects(
    board: str, keys: List[str], *args, **kwargs
) -> List[MockS3Object]:
    """Create a set of fake S3 objects."""
    template_link = (
        f"bin/{board}/en_US/adafruit-circuitpython-{board}-en_US-[version].uf2"
    )
    return [MockS3Object(template_link.replace("[version]", key)) for key in keys]


def test_get_board_versions() -> None:
    """Tests getting firmware versions for a given board."""
    board = "adafruit_feather_rp2040"
    language = "cs"
    expected_versions = [
        "6.2.0-beta.2",
        "6.2.0-beta.1",
        "6.2.0-beta.0",
    ]
    versions = circfirm.backend.s3.get_board_versions(board, language)
    assert versions == expected_versions


def test_get_board_versions_bad_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests getting only valid firmware versions for a given board."""
    board = "test_board"
    possible_versions = [
        "6.2.0-beta.2",
        "badversion",
        "6.2.0-beta.1",
        "6.2.0-beta.0",
    ]

    monkeypatch.setattr(
        boto3.resources.collection.CollectionManager,
        "filter",
        partial(get_fake_s3_objects, board, possible_versions),
    )

    expected_versions = possible_versions.copy()
    del expected_versions[1]

    versions = circfirm.backend.s3.get_board_versions(board)
    assert versions == expected_versions
