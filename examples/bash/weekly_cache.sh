# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board IDs in an array
BOARD_IDS=(
    "feather_m4_express"
    "feather_m0_express"
    "circuitplayground_express"
)

# Iterate for each board ID
for BOARD_ID in ${BOARD_IDS[*]}; do
    # Get the latest CircuitPython version for the board
    LATEST_VERSION=$(circfirm query latest $BOARD_ID)

    # Cache the determined version for the board
    circfirm cache save $BOARD_ID $LATEST_VERSION
done

# To make this script weekly, you can use crontab.
# The following line would run this script every Sunday at 9:00 am:
#
# 0 9 * * 0 /bin/bash /path/to/weeky_cache.sh
