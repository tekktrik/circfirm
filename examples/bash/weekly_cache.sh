# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board names in an array
BOARD_NAMES=(
    "feather_m4_express"
    "feather_m0_express"
    "circuitplayground_express"
)

# Iterate for each board name
for BOARD_NAME in ${BOARD_NAMES[*]}; do
    # Get the latest CircuitPython version for the board
    LATEST_VERSION=$(circfirm query latest $BOARD_NAME)

    # Cache the determined version for the board
    circfirm cache save $BOARD_NAME $LATEST_VERSION
done

# To make this script weekly, you can use crontab.
# The following line would run this script every Sunday at 9:00 am:
#
# 0 9 * * 0 /bin/bash /path/to/weeky_cache.sh
