..
   SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
   SPDX-License-Identifier: MIT

Viewing Important Filespaths
============================

You can see important filepaths used by ``circfirm`` using ``circfirm path``.

See ``circfirm path --help`` and ``circfirm path [command] --help`` for more information on commands.

Configuration Settings
----------------------

You can get the filepath of ``circfirm``'s configuration settings using ``circfirm path config``.

.. note::

    This is identical to the response given by ``circfirm config path``.

.. code-block:: shell

    # Get the configuration settings filepath
    circfirm path config

UF2 Archive
-----------

You can get the filepath of the UF2 archive folder using ``circfirm path archive``.

.. code-block:: shell

    # Get the UF2 archive folder filepath
    circifrm path archive

Local Plugins Folder
--------------------

You can get the filepath of the local plugins folder using ``circfirm path local-plugins``.

.. code-block:: shell

    # Get the local plugins folder filepath
    circfirm path local-plugins
