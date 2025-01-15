..
   SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
   SPDX-License-Identifier: MIT

Introduction to Plugins
=======================

``circfirm`` can be extended through the use of its plugin system.  Plugins allow you
to extend the CLI's capabilities beyond typical use cases and provided additional
functionalities you may want to use.

Below are general guidelines for downloading and configuring plugins, but see the
plugin's documentation for additional details.

Installing Plugins
------------------

Installing a plugin depends on how ``circfirm`` itself was installed.

pipx
^^^^

If you installed ``circfirm`` via ``pipx``, you will need to "inject" the plugin
into the same virtual environment as ``circfirm``.  This can typically be
achieved used the ``inject`` command:

.. code-block:: shell

    # Inject circfirm-plugin-name for circfirm
    pipx inject circfirm circfirm-plugin-name

pip
^^^

If you installed ``circfirm`` via ``pip``, you can simply using the ``install``
command to install the plugin into the same environment as ``circfirm``:

.. code-block:: shell

    # Install circfirm-plugin-name
    pip install circfirm-plugin-name

Activating Plugins
------------------

Activating a downloaded plugin can be done by adding an entry to the ``plugins.downloaded``
confirguration for ``circfirm``:

.. code-block:: shell

    # Activate plugin_name
    circfirm config add plugins.downloaded plugin_name

Note that the plugin name may not exactly match the download name of the plugin.  The name
added to ``plugins.downloaded`` should be a valid Python module import name - in fact, this
is exactly what is happening behind the scenes!  Check with the plugin provider for exact
details on what the plugin name is (as opposed to the download name).

.. note::

    This step is only needed if you downloaded the plugin.  Locally created plugins do not
    require activation.

Changing Configuration Settings
-------------------------------

Some plugins provide configuration files that can customize behavior similar to
``circfirm``.  You can view, edit, and otherwise interact with these settings by
using the ``--plugin`` option with the ``config`` command and it's various
sub-commands:

.. code-block:: shell

    # View the settings for plugin_name
    circfirm config view --plugin plugin_name

    # Edit a setting for plugin_name
    circfirm config edit --plugin plugin_name setting value

    # Reset the settings for plugin_name
    circfirm config reset --plugin plugin_name

Note while, conventionally, a plugin will have a single configuration file, sharing the same
name as the plugin, this may not be the case - it may use a different name or provide more
than one configuration file.  Please check with the plugin provider for additional details.
