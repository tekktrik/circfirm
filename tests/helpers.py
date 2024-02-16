# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Helpers for tests.

Author(s): Alec Delaney
"""

import circfirm.backend


def find_circuitpy() -> str:
    """Find the CIRCUITPY drive."""
    mount_location = circfirm.backend.find_circuitpy()
    assert mount_location is not None
    return mount_location
