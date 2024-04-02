# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Tests the backend configuration file functionality.

Author(s): Alec Delaney
"""

import pytest

import circfirm.backend.config


def test_cast_to_bool() -> None:
    """Tests casting a string value to a boolean."""
    assert circfirm.backend.config.cast_input_to_bool("true")
    assert not circfirm.backend.config.cast_input_to_bool("false")
    with pytest.raises(ValueError):
        _ = circfirm.backend.config.cast_input_to_bool("badvalue")


def test_cast_to_int() -> None:
    """Tests casting a string value to a boolean."""
    values = ("3", "-2", "0", "10000")
    for value in values:
        assert circfirm.backend.config.cast_input_to_int(value) == int(value)
    with pytest.raises(ValueError):
        _ = circfirm.backend.config.cast_input_to_int("badvalue")


def test_cast_to_float() -> None:
    """Tests casting a string value to a boolean."""
    values = ("0.123", "3.14151926", "-0.9993", "0.0")
    for value in values:
        assert circfirm.backend.config.cast_input_to_float(value) == float(value)
    with pytest.raises(ValueError):
        _ = circfirm.backend.config.cast_input_to_float("badvalue")
