# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board IDs in an array
$BOARD_IDS=@(
    "feather_m4_express",
    "feather_m0_express",
    "circuitplayground_express"
)

# Iterate for each board ID
for ($BOARD_INDEX = 0; $BOARD_INDEX -lt $BOARD_IDS.Count; $BOARD_INDEX++) {
    # Get the latest CircuitPython version for the board
    $LATEST_VERSION=(circfirm query latest $BOARD_IDS[$BOARD_INDEX])

    # Cache the determined version for the board
    circfirm cache save $BOARD_IDS[$BOARD_INDEX] $LATEST_VERSION
}

# To make this script weekly, you can use something like schtasks
# schtasks /create /tn 'Weekly Cache of Firmware' /tr \path\to\weekly_cache.ps1 /sc weekly /d SUN /st 09:00
