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

Saving the Latest Version
-------------------------

You can save the latest version of the CircuitPython firmware using ``circfirm cache latest``.

.. code-block:: shell

    # Save the latest CircuitPython version for the feather_m4_express board
    circfirm cache latest feather_m4_express

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

You can clear cached firmware versions using ``circfirm cache clear``.

You can also specify what should be cleared in terms of specific board IDs, versions, and languages
using the ``--board-id``, ``--version``, and ``--language`` options respectively.

If you would like to use regex for the board ID, version, and language, you can use the ``--regex``
flag.  The board ID pattern will be searched for **FROM THE BEGINNING** of the board ID (e.g., "hello"
**would not**  match "123hello123").  The version and language patterns will be searched for
**ANYWHERE** in the board ID (e.g., "hello" **would** match "123hello123") unless the pattern
specifies otherwise.  This is done so that:

- Matching board versions is generous (e.g., removing Feather board firmwares using ``feather``)
- Matching entire version sets more convenient without being too burdensome (e.g., using regex with
  the version pattern ``8`` is most likely an attempt to remove versions starting with 8 as opposed
  to containing an 8 anywhere in them)
- Matching languages is not too greedy with typos

.. code-block:: shell

    # Clear the cache
    circfirm cache clear

    # Clear the cache of French versions of the feather_m4_express
    circfirm cache clear --board-id feather_m4_express --language fr

    # Clear the cache of any board ID containing "feather" and all versions in the 8.2 release
    circfirm cache clear --regex --board-id feather --version "8\.2"
