#!/bin/bash

ESC="\x1B["

CLEAR="\x1B[2J"
CURSOR_HOME="\x1B[H"
BACKSPACE="\x08"

TESTS=(
"${CLEAR}${CURSOR_HOME}\nNew line.."
"123xxxyyy"
"${BACKSPACE}${BACKSPACE}${BACKSPACE}${BACKSPACE}${BACKSPACE}${BACKSPACE}"
"456789abc"
"${BACKSPACE}${BACKSPACE}${BACKSPACE}"
"Ending number here. v"
)

for string in "${TESTS[@]}"
do
    echo -en "${string}" > $1
    # sleep 0.8
    read -p "Press ENTER to continue."
done

read -p "Press ENTER to clean screen."
echo -en $CLEAR > $1
