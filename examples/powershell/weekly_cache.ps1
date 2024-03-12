# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board names in an array
$BOARD_NAMES=@(
    "feather_m4_express",
    "feather_m0_express",
    "circuitplayground_express"
)

# Iterate for each board name
for ($BOARD_INDEX = 0; $BOARD_INDEX -lt $BOARD_NAMES.Count; $BOARD_INDEX++) {
    # Get the latest CircuitPython version for the board
    $LATEST_VERSION=(circfirm query latest $BOARD_NAME)

    # Cache the determined version for the board
    circfirm cache save $BOARD_NAMES[$BOARD_INDEX] $LATEST_VERSION
}

# To make this script weekly, you can use something like schtasks
# schtasks /create /tn 'Weekly Cache of Firmware' /tr \path\to\weekly_cache.ps1 /sc weekly /d SUN /st 09:00
