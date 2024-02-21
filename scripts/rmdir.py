# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Cross-platform script for deleting folders in the CI/Makefile.

Author(s): Alec Delaney
"""

# pragma: no cover

import shutil
import sys

target = sys.argv[1]
shutil.rmtree(target)
