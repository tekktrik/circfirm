..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Checking the Current Version
============================

You can get information about a currently connected board using ``circfirm current``.

See ``circfirm current --help`` and ``circfirm current [command] --help`` for more information on commands.

Getting the Board ID
--------------------

You can get the board ID of the currently connected board using ``circfirm current board-id``.

.. code-block:: shell

    # Get the board ID of the connected board
    circfirm current board-id

Getting the Firmware Version
----------------------------

You can get the CircuitPython version of the currently connected board using ``circfirm current version``.

.. code-block:: shell

    # Get the firmware version of the connected board
    circfirm current verson
