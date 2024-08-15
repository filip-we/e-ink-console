import logging
import pytest

import fcntl
import termios
import os
import time
import struct

from e_ink_console.screen import clear_screen, write_buffer_to_screen
from console import ConsoleSettings, main_loop

log = logging.getLogger(__name__)

@pytest.mark.parametrize(
    "rows,cols,test_bytes",
    [
        [
            40, 80,
            b"\x1B[2J\x1B[H0        1         2         3         4         5         6         7         8\
            \x1B[10;0H1\
            \x1B[20;0H2_._._Hej,hej,hej\
            \x1B[30;0H3\
            \x1B[39;0H39\
            \x1B[2;2Hxxx\x1B[3;2Hx x\x1B[4;2Hxxx\x1B[3;3H",
        ],
        [
            40, 80,
            b"\x1B[2J\x1B[0;0HCursor at 1,1\x1B[1;1H",
        ],
        [
            40, 80,
            b"\x1B[2J\x1B[H1234||\n..../?()gJ\nJJ||__^% ----\n||||",
        ],
    ],
)
def test_terminal_e2e(terminal_nr, it8951_driver, font_file,
    rows, cols, test_bytes):
    settings = ConsoleSettings(
        rows=rows,
        cols=cols,
        font_file=font_file,
        font_size=16,
        screen_width=1200,
        screen_height=825,
    )
    size = struct.pack("HHHH", settings.rows, settings.cols, 0, 0)
    with open(f"/dev/tty{terminal_nr}", "wb") as file_buffer:
        fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)

    clear_screen(settings.screen_height, settings.screen_width, it8951_driver)

    with open(f"/dev/tty{terminal_nr}", "wb") as fb:
        fb.write(test_bytes)

    time.sleep(1.8)

    with open(f"/dev/vcs{terminal_nr}", 'rb') as vcsu_buffer:
        buff = vcsu_buffer.read()

    with open(f"/dev/vcsa{terminal_nr}", 'rb') as vcsa_buffer:
        attributes = vcsa_buffer.read(4)

    rows, cols, cursor_col, cursor_row = list(map(ord, struct.unpack('cccc', attributes)))
    cursor = (cursor_row, cursor_col)
    log.info(f"The cursor is currently at row {cursor_row}, col {cursor_col}.")

    write_buffer_to_screen(
        settings=settings,
        old_buff=b"",
        buff=buff,
        old_cursor=(9, 9),
        cursor=cursor,
        character_encoding_width=1,
        font=settings.font,
        encoding="utf-8",
        it8951_driver=it8951_driver,
    )

    log.info("Waiting a short moment to let you verify the screen...")
    time.sleep(2)
    raise IOError
