..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Updating to the Latest Version
==============================

You can update the CircuitPython version of a connected board using ``circfirm update``.

See ``circfirm update --help`` for more information.

The board should be connected so it shows up as a CIRCUITPY USB drive (or equivalently named),
where the board ID will be read from the ``boot_out.txt`` file.  The CLI will then prompt you to set the
board into bootloader mode, after which the selected CircuitPython version will be installed on
the board.

If you wish to skip the step where the board ID is collected and simply connected the board in
bootloader mode, you can do so and simply use the ``--board-id`` option to provide the board ID.

You can specify a language using the ``--language`` option - the default is US English.

If you would like to include pre-releases as potential update versions, you can use the
``--pre-release`` flag.

If you would like to limit updates to only the latest minor or patch update from the current version,
you can use either the ``--limit-to-minor`` or ``--limit-to-patch`` flags respectively.  Note that if
both are used, the more limiting flag (``--limit-to-patch``) will take precedence.

.. note::

    This command will not update the board if the detected version of CircuitPython on the connected
    board is greater than or equal to updated version.

.. code-block:: shell

    # Update CircuitPython on the connected board
    circfirm update

    # Update the French translation of CircuitPython on the connected board
    circfirm --language fr

    # Update CircuitPython 8.0.0 on the connected Adafruit QT Py ESP32 Pico (in bootloader mode)
    circfirm update --board-id adafruit_qtpy_esp32_pico

    # Update CircuitPython on the connected board, considering pre-release versions
    circfirm update --pre-release
