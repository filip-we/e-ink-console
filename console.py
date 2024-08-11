import logging

import os
import struct
import sys
import subprocess
import fcntl
import termios
import tempfile
import time

from dataclasses import dataclass
from PIL import ImageFont
from e_ink_console.text_to_image import (
    get_contained_text_area,
    get_blank_image,
    get_terminal_update_image,
    identify_changed_text_area,
)


log = logging.getLogger()
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(ch)


@dataclass
class ConsoleSettings():
    rows: int
    cols: int
    screen_width: int
    screen_height: int
    font_path: str
    font_height: int = 16
    font_width: int = 8


def split(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]

def setup(settings, tty, it_8951_driver_program):
    # Check valid vcsa
    try:
        os.stat(vcsa)
        os.stat(tty)
    except OSError:
        log.critical("Error with {vcsa} or {tty}.")
        exit(1)

    size = struct.pack("HHHH", settings.rows, settings.cols, 0, 0)
    with open(tty, 'wb') as file_buffer:
        fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)

    image = get_blank_image(settings.screen_height, settings.screen_width)
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "background.png"), "wb") as fb:
            image.save(fb)
            update_screen(
                settings.screen_height,
                settings.screen_width,
                fb.name,
                0,
                0,
                it_8951_driver_program,
            )

def update_screen(screen_height, screen_width, image_file_path, pos_height, pos_width, program):
    cmd = [program, image_file_path, str(pos_width), str(pos_height)]
    log.debug(f"Calling IT8951-drivers with arguments: {cmd}")
    p = subprocess.run(" ".join(cmd),
        shell=True,
        check=True,
    )


def main_loop(vcsa, tty, font, font_height, font_width, it_8951_driver_program):
    character_encoding_width = 1
    encoding = "utf-8"
    old_buff = b''
    old_cursor = (-1, -1)

    while True:
        with open(vcsa.replace("vcsa", "vcs"), 'rb') as vcsu_buffer:
            buff = vcsu_buffer.read()

        with open(vcsa, 'rb') as vcsa_buffer:
            attributes = vcsa_buffer.read(4)

        rows, cols, cursor_col, cursor_row = list(map(ord, struct.unpack('cccc', attributes)))
        cursor = (cursor_row, cursor_col) #, char_under_cursor.decode(encoding, 'ignore'))

        if buff == old_buff and cursor == old_cursor:
            time.sleep(2)
            ("skipping update")
            continue

        log.debug(f"Cursor {cursor}")
        log.debug(f"Buff length {len(buff)}")
        log.debug(f"Rows, cols: {rows, cols}")

        changed_sections = identify_changed_text_area(old_buff, buff, rows, cols)
        log.debug(f"changed_sections {changed_sections}")

        contained_text_area = get_contained_text_area(changed_sections, old_cursor, cursor)
        log.debug(f"contained_text_area {contained_text_area}")

        decoded_buff_list = split(buff.decode(encoding, "replace"), cols * character_encoding_width)

        image = get_terminal_update_image(
            decoded_buff_list,
            contained_text_area,
            font,
            font_height,
            font_width,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "buffer.png"), "wb") as fb:
                image.save(fb)
                update_screen(
                    settings.screen_height,
                    settings.screen_width,
                    fb.name,
                    contained_text_area[0] * font_height,
                    contained_text_area[2] * font_width,
                    it_8951_driver_program,
                )

        old_buff = buff
        old_cursor = cursor


if __name__ == "__main__":
    vcsa = "/dev/vcsa" + sys.argv[1]
    tty = "/dev/tty" + sys.argv[1]
    font_path = sys.argv[2]
    it8951_driver_program = sys.argv[3]

    settings = ConsoleSettings(
        rows=40,
        cols=80,
        font_path=font_path,
        font_height=16,
        font_width=8,
        screen_width=1200,
        screen_height=825,
    )
    setup(settings, tty, it8951_driver_program)

    font = ImageFont.truetype(settings.font_path, settings.font_height)

    main_loop(vcsa, tty, font, settings.font_height, settings.font_width, it8951_driver_program)
