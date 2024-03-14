..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Installing Specific Versions
============================

You can install different CircuitPython versions to a connected board using ``circfirm install``.

See ``circfirm install --help`` for more information.

The board should be connected so it shows up as a CIRCUITPY USB drive (or equivalently named),
where the board ID will be read from the ``boot_out.txt`` file.  The CLI will then prompt you to set the
board into bootloader mode, after which the selected CircuitPython version will be installed on
the board.

If you wish to skip the step where the board ID is collected and simply connected the board in
bootloader mode, you can do so and simply use the ``--board-id`` option to provide the board ID.

You can specify a language using the ``--language`` option - the default is US English.

.. code-block:: shell

    # Install CircuitPython 8.0.0 on the connected board
    circfirm install 8.0.0

    # Install the French translation of CircuitPython on the connected board
    circfirm install 8.0.0 --language fr

    # Install CircuitPython 8.0.0 on the connected Adafruit QT Py ESP32 Pico (in bootloader mode)
    circfirm install 8.0.0 --board-id adafruit_qtpy_esp32_pico
