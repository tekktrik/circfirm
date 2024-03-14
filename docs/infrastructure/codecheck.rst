..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Code Checking
=============

Code checks are performed using ``pre-commit``, which runs git pre-commit hooks on all files.

If you are developing the ``circfirm`` codebase, you can install these hooks into git by
runing ``pre-commit install``.

You can manually perform a check of the code, which includes all of the items below, by
running ``make check``.

Linting & Formatting
--------------------

Linting and formatting are done using ``ruff`` pre-commit hooks, as well as some of
the basic ``pre-commit`` ones provided by the project.

You can manually run linting and formatting checks using ``make lint`` and ``make format``
respectively.

Secret Detection
----------------

Yelp's ``detect-secrets`` tool runs to try and prevent secrets from being accidentally
committed and shared.

Open Source Compliance
----------------------

The FSF's REUSE tool runs on the entire repository to make sure all files are properly
labelled with an open source license and conform to REUSE standards, which makes it
easier for other people to reuse any part of it.
