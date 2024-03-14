..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Querying Boards and Versions
============================

You can query for valid board IDs and CircuitPython versions from online resources using ``circfirm query``.

See ``circfirm query --help`` and ``circfirm query [command] --help`` for more information on commands.

Querying Board IDs
------------------

You can query a list of valid board IDs from the CircuitPython GitHub repository using ``circfirm query board-ids``.

You can use the ``--regex`` option to further select boards from the list matching a provided regex pattern.
The pattern will be searched for **ANYWHERE** in the board ID (e.g., "hello" **would** match "123hello123") unless
the pattern specifies otherwise.

.. note::

    Querying board IDs communicates with GitHub, which can only be done 60 times per hour unauthenticated.
    If you plan to make frequent use of this command consider adding a GitHub token to the configuration
    settings (``circfirm config edit token.github <your-token-here>``).

.. code-block:: shell

    # List all board IDs
    circfirm query board-ids

    # List all board IDs containing the phrase "pico"
    circfirm query board-ids --regex pico

Querying Board Versions
-----------------------

You can query a list of CircuitPython versions for a board ID in the official AWS S3 bucket of firmware
using ``circfirm query version``.

You can use the ``--regex`` option to further select versions from the list matching a provided regex pattern.
The pattern will be searched for **FROM THE BEGINNING** in the board ID (e.g., "hello" **would not**  match "123hello123").
This is done to make matching entire version sets more convenient ("8\.2\..+" matches the entirety of 8.2 and all associated
minor, alpha, beta and release candidate versions).

You can also set the language using the ``--language`` option, which can affect the list of available versions.

.. code-block:: shell

    # List all available versions for the Feather M4 Express
    circfirm query versions feather_m4_express

    # List all available French versions for the Feather M4 Express
    circfirm query versions feather_m4_express --language fr

    # List all versions in the 8.2.X set for the Feather M4 Express
    circfirm query versions feather_m4_express --regex 8\.2\..+

Query the Latest Version
------------------------

You can query the latest version of CircuitPython use ``circfirm query latest``

This command take a board ID as an argument, as this may have an effect on available CircuitPython versions.
For simplicity, if information is not needed about a specific board but rather the CircuitPython project as
a whole, the default board ID ``raspberry_pi_pico`` is used, as it is an actively supported board.

You can also set the language using the ``--language`` option, which can affect the list of available versions.

If you would like to include pre-release versions as potential latest versions, you can use the
``--pre-release`` flag.

.. code-block:: shell

    # Get the latest version of CircuitPython
    circfirm query latest

    # Get the latest version of CircuitPython for the Feather M4 Express
    circfirm query latest feather_m4_express

    # Get the latest version of CircuitPython for the Feather M4 Express, including pre-releases
    circfirm query latest feather_m4_express --pre-release
