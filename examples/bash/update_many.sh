# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

# Store the board ID and quantity in variables for use throughout the script
BOARD_ID=feather_m4_express
BOARD_QUANTITY=10

# Initialize some variables we'll use to handle the programming sequence
LOAD_FIRMWARE=true
REPEAT_ASK=true

# Run thhis sequence up to BOARD_QUANTITY times
for BOARD_NUM in $(seq 1 $BOARD_QUANTITY); do

    # Update the connected board (which is in bootloader mode)
    circfirm update --board-id $BOARD_ID

    # If the update command failed, exit out of the script
    if [[ $? ]]; then
        exit 1
    fi

    # If that was the last update, we're done!
    if [[ $BOARD_NUM == $BOARD_QUANTITY ]]; then
        exit
    fi

    # Ask whether another update should be performed
    REPEAT_ASK=true
    while [[ $REPEAT_ASK == true ]]; do

        # Read a single character from the terminal
        read -r -N1 -p "Continue? [Y/n] " CHAR_RESPONSE

        # Check and handle the response from the user
        case $CHAR_RESPONSE in
            # Y, y, or space character
            y | Y | " ")
                echo ""
                LOAD_FIRMWARE=true
                REPEAT_ASK=false
                ;;
            # Enter character
            $'\n')
                LOAD_FIRMWARE=true
                REPEAT_ASK=false
                ;;
            # N or n character
            n | N)
                echo ""
                LOAD_FIRMWARE=false
                REPEAT_ASK=false
                ;;
            # Any other character (invaid, ignore)
            *)
                echo ""
                echo "Invalid response"
        esac
    done

    # If the next update was cancelled, end the script
    if [[ $LOAD_FIRMWARE == false ]]; then
        exit
    fi

done
