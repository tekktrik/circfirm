..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Caching Versions
================

You can interact with the local cache of CircuitPython firmware versions using ``circfirm cache``.

See ``circfirm cache --help`` and ``circfirm cache [command] --help`` for more information on commands.

Saving Versions
---------------

You can save versions of the CircuitPython firmware using ``circfirm cache save``.

.. code-block:: shell

    # Save the CircuitPython 8.0.0 firmware for the feather_m4_express board
    circfirm cache save feather_m4_express 8.0.0

Listing Versions
----------------

You can list cached versions of the CircuitPython firmware using ``circfirm cache list``.

.. code-block:: shell

    # List all the firmware versions
    circfirm cache list

    # List all the firmware versions for the feather_m4_express board
    circfirm cache list --board-id feather_m4_express

Clearing the Cache
------------------

You can clearr cached firmware versions using ``circfirm cache clear``.

You can also specify what should be cleared in terms of board IDs, versions, and languages.

.. code-block:: shell

    # Clear the cache
    circfirm cache clear

    # Clear the cache of French versions of the feather_m4_express
    circfirm cache clear --board-id feather_m4_express --language fr
