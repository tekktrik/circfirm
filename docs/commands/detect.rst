..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Detecting Connected Boards
==========================

You can detect connected CircuitPython boards using ``circfirm detect``.

See ``circfirm detect --help`` and ``circfirm detect [command] --help`` for more information on commands.

Detecting a CIRCUITPY Board
---------------------------

You can detect a connected CircuitPython board in CIRCUITPY or equivalent mode using ``circfirm detect circuitpy``.

.. code-block:: shell

    # Detect a connected board in CIRCUITPY (or equivalent) mode
    circfirm detect circuitpy

Detecting a Bootloader Board
----------------------------

You can detect a connected CircuitPython board in bootloader mode using ``circfirm detect bootloader``.

.. code-block:: shell

    # Detect a connected board in bootloader mode
    circfirm detect bootloader
