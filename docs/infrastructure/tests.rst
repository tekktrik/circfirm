..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Testing & Code Coverage
=======================

The project contains test code for testing compliance of the tool with
expected behavior.  Testing is done using coverage.py, which uses pytest
to actually run the tests.  Coverage.py then analyzes the code that was
run in both the source code and tests themselves to calculate the code
coverage metric.

In the :ref:`build CI <build-ci>` for pull requests, this code coverage
metric is uploaded to Codecov, which then comments on the pull request
to help identify whether additional tests are needed based on the
changes.
