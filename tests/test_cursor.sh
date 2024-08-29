#!/bin/bash

ESC="\033["

CLEAR="\033[2J"
CURSOR_HOME="\033[H"
VAR="Cursor at Home position."

TESTS=(
#"${CURSOR_HOME}Hello, world!"
"${CLEAR}\033[0;0H0        1         2         3         4         5         6         7         8\033[10;0H1\033[20;0H2\033[30;0H3\033[39;0H39"
"hej hej"
"hej igen"
"${CLEAR}${CURSOR_HOME}Let's clean the screen and write some stuff."
)

for string in "${TESTS[@]}"
do
    read -p "Press ENTER to run next test."
    echo -e "${string}" > $1
done
