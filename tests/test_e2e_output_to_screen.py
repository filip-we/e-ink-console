import logging
import pytest

import fcntl
import termios
import os
import time
import struct

from PIL import Image, ImageDraw

from e_ink_console.screen import clear_screen, write_buffer_to_screen
from e_ink_console.terminal import TerminalSettings, main_loop

from e_ink_console.text_to_image import (
    get_partial_terminal_image,
)
log = logging.getLogger(__name__)

log = logging.getLogger(__name__)


TESTS_DIR = os.path.abspath(os.path.join(__file__, os.pardir))

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
    settings = TerminalSettings(
        tty=f"/dev/tty{terminal_nr}",
        vcsa=f"/dev/vcsa{terminal_nr}",
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
        it8951_driver=it8951_driver,
    )

    log.info("Waiting a short moment to let you verify the screen...")
    time.sleep(2)


@pytest.mark.parametrize(
    "name,text_area",
    [
        ["all_screen", (0, 0, 3, 9)],
        ["start_of_row_0", (0, 0, 0, 2)],
        ["middle_of_row_0", (0, 2, 0, 4)],
    ],
)
def test_font_drawing(font_file, name, text_area):
    settings = TerminalSettings(
        tty="/dev/tty9999",
        vcsa="/dev/vcsa9999",
        rows=4,
        cols=10,
        font_file=font_file,
        font_size=16,
        screen_width=1200,
        screen_height=825,
    )

    buffer_list = [
        "abcdefghij",
        "          ",
        "0123456789",
        "          ",
    ]

    image = get_partial_terminal_image(
        settings=settings,
        buffer_list=buffer_list,
        text_area=text_area,
        cursor=(0, 0),
        spacing=0,
    )

    with open(os.path.join(TESTS_DIR, "output", name + ".png"), "wb") as fb:
        image.save(fb)
