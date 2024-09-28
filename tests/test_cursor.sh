#!/bin/bash

ESC="\x1B["

CLEAR="\x1B[2J"
CURSOR_HOME="\x1B[H"
BACKSPACE="\x08"

VAR="Cursor at Home position."

TESTS=(
#"${CURSOR_HOME}Hello, world!"
"${CLEAR}\x1B[0;0H0        1         2         3         4         5         6         7         8\x1B[10;0H1\x1B[20;0H2\x1B[30;0H3\x1B[39;0H39"
"hej hej"
"hej igen"
"${CLEAR}${CURSOR_HOME}Let's clean the screen and write some stuff."
"${CLEAR}${CURSOR_HOME}Clean the screen, then let's send four backspaces! 1234"
"${BACKSPACE}${BACKSPACE}${BACKSPACE}${BACKSPACE}"
"Now we should be printing neatly after the exclamation mark."
)

for string in "${TESTS[@]}"
do
    read -p "Press ENTER to run next test."
    echo -en "${string}" > $1
done
