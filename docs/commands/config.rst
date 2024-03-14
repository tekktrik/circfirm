..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

Configuring the CLI
===================

You can modify the CLI configurations settings using ``circfirm config``.

See ``circfirm config --help`` and ``circfirm config [command] --help`` for more information on commands.

View Settings
-------------

You can view configuration settings using ``circfirm config view``.

You can view all the settings, a subset, or just a specific one.  Subsettings are accessed using period separators.

.. code-block:: shell

    # View all the configuration settings
    circfirm config view

    # View a specific setting
    circfirm config view output.supporting.silence

Edit Settings
-------------

You can edit configuration settings using ``circfirm config view``.

You must edit a specific setting at a time.  Subsettings are accessed using period separators.

.. code-block:: shell

    # Edit a configuration settings with a value
    circfirm config edit output.supporting.silence true

Reset Settings
--------------

You can reset the configuration settings to the default using ``circfirm config reset``.

.. code-block:: shell

    # Reset the configuration settings to the default
    circfirm config reset
