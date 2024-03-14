# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Backend functionality for the working with CircuitPython GitHub repository.

Author(s): Alec Delaney
"""

import datetime
import re
from typing import List, Tuple, TypedDict

import requests

BASE_REQUESTS_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BOARDS_REGEX = r"ports/.+/boards/([^/]+)"


class RateLimit(TypedDict):
    """Format of a rate limit dictionary."""

    limit: int
    remaining: int
    reset: int
    used: int
    resource: str


class GitTreeItem(TypedDict):
    """Format of a git tree item dictionary."""

    path: str
    mode: str
    type: str
    size: int
    sha: str
    url: str


def get_rate_limit() -> Tuple[int, int, datetime.datetime]:
    """Get the rate limit for the GitHub REST endpoint."""
    response = requests.get(
        url="https://api.github.com/rate_limit",
        headers=BASE_REQUESTS_HEADERS,
    )
    limit_info: RateLimit = response.json()["rate"]
    available: int = limit_info["remaining"]
    total: int = limit_info["limit"]
    reset_time = datetime.datetime.fromtimestamp(limit_info["reset"])
    return available, total, reset_time


def get_board_id_list(token: str) -> List[str]:
    """Get a list of CircuitPython boards."""
    boards = set()
    headers = BASE_REQUESTS_HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        url="https://api.github.com/repos/adafruit/circuitpython/git/trees/main",
        params={
            "recursive": True,
        },
        headers=headers,
    )
    try:
        tree_items: List[GitTreeItem] = response.json()["tree"]
    except KeyError as err:
        raise ValueError("Could not parse JSON response, check token") from err
    for tree_item in tree_items:
        if tree_item["type"] != "tree":
            continue
        result = re.match(BOARDS_REGEX, tree_item["path"])
        if result:
            boards.add(result[1])
    return sorted(boards)
