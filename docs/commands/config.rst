..
   SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
   SPDX-License-Identifier: MIT

Configuring the CLI
===================

You can modify the CLI configurations settings using ``circfirm config``.

See ``circfirm config --help`` and ``circfirm config [command] --help`` for more information on commands.

For a list of settings and their explanations, see the :ref:`Configuration Settings<config-settings>` page.

You can interact with plugin settings by adding the ``--plugin <name>`` option to any of the commands below.

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

You can edit configuration settings using ``circfirm config edit``.

You must edit one specific setting at a time.  Subsettings are accessed using period separators.

.. code-block:: shell

   # Edit a configuration settings with a value
   circfirm config edit output.supporting.silence true

.. _config-editor:

Edit Settings via Editor
^^^^^^^^^^^^^^^^^^^^^^^^

For a more native editing experience using the built-in text editor, you can use ``circfirm config editor``.

.. code-block:: shell

   # Edit the configuration settings in the native text editor
   circfirm config editor

Add/Remove from List
--------------------

You can add or remove a string value to a list using ``circfirm config add`` and ``circfirm config remove``
respectively.

.. code-block:: shell

   # Add the circfirm_hello_world plugin to the plugins.downloaded setting
   circfirm config add plugin.downloaded circfirm_hello_world

   # Remove the circfirm_hello_world plugin from the plugins.downloaded setting
   circfirm config remove plugin.downloaded circfirm_hello_world

Get Configuration Filepath
--------------------------

You can see where a configruation file is located using ``circfirm config path``.

.. code-block:: shell

   # See where the configuration file for circfirm is located
   circfirm config path

   # See where the configuration file for the circfirm_hello_world plugin is located
   circfirm config path --plugin circfirm_hello_world

Reset Settings
--------------

You can reset the configuration settings to the default using ``circfirm config reset``.

.. code-block:: shell

   # Reset the configuration settings to the default
   circfirm config reset
