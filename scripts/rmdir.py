# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Cross-platform script for deleting folders in the CI/Makefile.

Author(s): Alec Delaney
"""

# pragma: no cover

import os
import shutil
import sys

target = sys.argv[1]

for root, dirs, files in os.walk(target):
    children = dirs + files
    for name in children:
        filepath = os.path.join(root, name)
        os.chmod(filepath, 0o777)

shutil.rmtree(target)
