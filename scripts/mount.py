# SPDX-FileCopyrightText: 2026 Alec Delaney
# SPDX-License-Identifier: MIT

"""Cross-platform script for determining mount information.

Author(s): Alec Delaney
"""

import json
import platform
import sys

system = platform.system()
n = int(sys.argv[1])
info = int(sys.argv[2])

with open("scripts/info.json") as jsonfile:
    contents = json.load(jsonfile)

print(contents[system][n][info])
