..
    SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
    SPDX-License-Identifier: MIT

CI/CD Pipeline
==============

.. _build-ci:

Build CI
--------

When code is pushed to the repository or a pull request is submitted, it will
trigger a GitHub Actions run of the build CI, which can be found in
``.github/workflows/push.yml``.  This build CI performs the following checks:

- Code quality
- Packaging build
- Code testing
- Code coverage

You can read more about the code checks performed :doc:`here <codecheck>`

CodeQL CI
---------

Similar to the build CI, a GitHub Actions performs a CodeQL check on the code
whenever code is pushed to the repository or a pull request is submitted.
Additionally, it runs this action daily to ensure best practices and look for
issues as CodeQL is improved.

.. _publish-ci:

Publish CI
----------

When a release is made on GitHub for the project, it builds the project using
the Python ``build`` package.  Before building, the publish CI pushes the
release tag to the ``VERSION`` file.  The CI then uses ``build`` to generate
both source and binary distributions of the project.  The CU then uploads
these distributions to PyPI for download through tools such as ``pipx`` and
``pip``.
