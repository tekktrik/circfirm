..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Detecting Connected Boards
==========================

You can detect and return information from connected CircuitPython boards using ``circfirm devices``.

See ``circfirm devices --help`` and ``circfirm devices [command] --help`` for more information on commands.

Detecting All Boards
--------------------

You can detect connected boards in either CIRCUITPY (or equivalent) or bootloader mode using ``circfirm devices``.

.. code-block:: shell

    # Detect connected boards
    circfirm devices

Detecting Only CIRCUITPY Boards
-------------------------------

You can detect connected CircuitPython boards in CIRCUITPY or equivalent mode using ``circfirm devices circuitpy``.

.. code-block:: shell

    # Detect connected boards in CIRCUITPY (or equivalent) mode
    circfirm devices circuitpy

You many just want the paths to specific boards for scription purposes.  You can do this using the ``--paths-only`` option.

.. code-block:: shell

    # Detect connected boards in CIRCUITPY (or equivalent) mode
    circfirm devices circuitpy --paths-only

Detecting Only Bootloader Boards
--------------------------------

You can detect connected CircuitPython boards in bootloader mode using ``circfirm devices bootloader``.

.. code-block:: shell

    # Detect connected boards in bootloader mode
    circfirm devices bootloader
