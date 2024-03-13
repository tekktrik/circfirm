# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board ID and quantity in variables for use throughout the script
$BOARD_ID='feather_m4_express'
$BOARD_QUANTITY=10

# Initialize some variables we'll use to handle the programming sequence
$LOAD_FIRMWARE=$true
$REPEAT_ASK=$true

# Run thhis sequence up to BOARD_QUANTITY times
for ($BOARD_NUM=1; $BOARD_NUM -le $BOARD_QUANTITY; $BOARD_NUM++) {

    # Update the connected board (which is in bootloader mode)
    circfirm update --board-id $BOARD_ID

    # If the update command failed, exit out of the script
    if ($LASTEXITCODE -eq 0) {
        exit 1
    }

    # If that was the last update, we're done!
    if ($BOARD_NUM -eq $BOARD_QUANTITY) {
        exit
    }

    # Ask whether another update should be performed
    $REPEAT_ASK=$true
    while ($REPEAT_ASK) {

        # Read a single character from the terminal
        write-host -nonewline "Continue? [Y/n]: "
        $CHAR_RESPONSE = $Host.UI.RawUI.ReadKey().Character

        # Check and handle the response from the user
        switch -Regex ($CHAR_RESPONSE) {
            # Y, y, or space character
            '^(y|Y| )' {
                write-output ""
                $LOAD_FIRMWARE=$true
                $REPEAT_ASK=$false
            }
            # Enter character
            '^(\n)' {
                $LOAD_FIRMWARE=$true
                $REPEAT_ASK=$false
            }
            # N or n character
            '^(n|N)' {
                write-output ""
                $LOAD_FIRMWARE=$false
                $REPEAT_ASK=$false
            }
            # Any other character (invaid, ignore)
            default {
                write-output ""
                write-output "Invalid response"
            }
        }
    }

    # If the next update was cancelled, end the script
    if (!$LOAD_FIRMWARE) {
        exit
    }

}
