..
   SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
   SPDX-License-Identifier: MIT

.. _config-settings:

Configuration Settings
======================

Settings can be configured using the ``config`` command.  Each setting is ASCII text, with
sub-settings accessed using periods (e.g., ``category.setting.subsetting``).  To see the full
settings file, you can use ``circfirm config view``.

Below is a more in-depth reference for each of the settings:

Tokens (``token``)
------------------

GitHub Token (``token.github``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you'd like to add a GitHub token to enable authenticated requests when using the ``query``
command, you can add a GitHub token here.  You can read `GitHub's documentation on tokens
<https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_
for more information on how tokens work and how to create them.

Output Modification (``output``)
--------------------------------

You can optionally silence relevant supporting and warning text responses by setting ``silence``
to ``true`` each of the respective configuration settings (``output.supporting.silence`` and
``output.warning.silence``).  This may be useful when writing bash scripts that will parse
responses output by ``circfirm``.

Editor (``editor``)
-------------------

You can change the in-terminal editor used by ``circfirm config editor`` (:ref:`reference<config-editor>`) by setting this to
the path of an alternative editor.

Plugins (``plugins``)
---------------------

Downloaded plugins (``plugins.downloaded``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have downloaded plguins (i.e., from PyPI), you can activate and use them by adding their
respective import names here.  This is likely to be their name with dashes replaced by underscores,
but you should check the plugin's documentation to see what value should be used.  This is
especially true if the donwloaded plugin library provides multiple plugins.
