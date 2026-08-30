..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Checking the Current Version
============================

You can get information about a currently connected board using ``circfirm info``.

See ``circfirm info --help`` and ``circfirm info [command] --help`` for more information on commands.

Getting All Board information
-----------------------------

You can get all information from the board using ``circfirm info {DEVICE_PATH}``.

.. tabs::

    .. group-tab:: Windows

        .. code-block:: shell

            # Get the board information
            circfirm info T:\

    .. group-tab:: macOS

        .. code-block:: shell

            # Get the board information
            circfirm info /Volumes/CIRCUITPY

    .. group-tab:: Linux

        .. code-block:: shell

            # Get the board information
            circfirm info /run/media/tekktrik/CIRCUITPY



Getting Only the Board ID
-------------------------

You can get the board ID of the currently connected board using ``circfirm info {DEVICE_PATH} board-id``.

.. tabs::

    .. group-tab:: Windows

        .. code-block:: shell

            # Get the board ID of the connected board
            circfirm info T:\ board-id

    .. group-tab:: macOS

        .. code-block:: shell

            # Get the board ID of the connected board
            circfirm info /Volumes/CIRCUITPY board-id

    .. group-tab:: Linux

        .. code-block:: shell

            # Get the board ID of the connected board
            circfirm info /run/media/tekktrik/CIRCUITPY board-id

Getting Only the Firmware Version
---------------------------------

You can get the CircuitPython version of the currently connected board using ``circfirm info {DEVICE_PATH} version``.

.. tabs::

    .. group-tab:: Windows

        .. code-block:: shell

            # Get the firmware version of the connected board
            circfirm info T:\ version

    .. group-tab:: macOS

        .. code-block:: shell

            # Get the firmware version of the connected board
            circfirm info /Volumes/CIRCUITPY version

    .. group-tab:: Linux

        .. code-block:: shell

            # Get the firmware version of the connected board
            circfirm info /run/media/tekktrik/CIRCUITPY version
