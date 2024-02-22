circfirm
--------

.. image:: https://img.shields.io/pypi/pyversions/circfirm
   :target: https://pypi.org/project/circfirm/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/github/actions/workflow/status/tekktrik/circfirm/push.yml
   :target: https://github.com/tekktrik/circfirm/actions
   :alt: GitHub Actions Workflow Status

.. image:: https://codecov.io/gh/tekktrik/circfirm/graph/badge.svg?token=UM67L1VZZ1
   :target: https://codecov.io/gh/tekktrik/circfirm
   :alt: Codecov Report

.. image:: https://img.shields.io/pypi/wheel/circfirm
   :target: https://pypi.org/project/circfirm/
   :alt: PyPI - Wheel

.. image:: https://img.shields.io/pypi/dm/circfirm
   :target: https://pypi.org/project/circfirm/
   :alt: PyPI - Downloads

A CLI tool for updating the firmware for CircuitPython boards

Installation
============

The best way to install ``circfirm`` is by using `pipx <https://github.com/pypa/pipx>`_,
which creates an isolated virtual environment for the dependencies:

.. code-block:: shell

    pipx install circfirm

You can also just use ``pip`` to install it, if the dependencies won't cause issues:

.. code-block:: shell

    pip install circfirm

Usage
=====

The follow commands show some of the functionality of ``circfirm``:

.. code-block:: shell

    # Install a version of CircuitPython to a connected board
    circfirm install 8.0.0

    # Install a version of CircuitPython in French to a connected board
    circfirm install 8.0.0 --language fr

    # List all the cached (previously downloaded) CircuitPython versions
    circfirm cache list

    # List all the cached CircuitPython versions for a speciic board
    circfirm cache list --board feather_m4_express

    # Save a version of CircuitPython to the cache
    # (You can also use the --language option here)
    circfirm cache save feather_m4_express 8.0.0

    # Clear the cached CircuitPython versions
    circfirm cache clear

    # You can use --board, --version, and --language options to further specify
    # what firmwares should be cleared - this clears version 7.0.0 firmwares for
    # all boards and in all languages
    circfirm cache clear --version 7.0.0

    # See help/information about circfirm or any specific command using --help
    circfirm --help
    circfirm install --help
    circfirm cache save --help
