import logging

import click
import os
import struct
import sys
import fcntl
import termios
import tempfile
import time

from PIL import ImageFont

from e_ink_console.screen import write_buffer_to_screen


log = logging.getLogger()
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(ch)


class ConsoleSettings():
    def __init__(self,
        rows: int,
        cols: int,
        screen_width: int,
        screen_height: int,
        font_file: str,
        font_height: int = 16,
        font_width: int = 8,
    ):
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_file =  font_file
        self.font_height = font_height
        self.font_width = font_width
        self.font = ImageFont.truetype(font_file, self.font_height)


def setup(settings, tty, vcsa):
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

def main_loop(terminal_nr, settings, it8951_driver_program):
    vcsa = "/dev/vcsa" + terminal_nr
    tty = "/dev/tty" + terminal_nr
    character_encoding_width = 1
    encoding = "utf-8"
    old_buff = b''
    old_cursor = (-1, -1)

    setup(settings, tty, vcsa)

    while True:
        with open(vcsa.replace("vcsa", "vcs"), 'rb') as vcsu_buffer:
            buff = vcsu_buffer.read()

        with open(vcsa, 'rb') as vcsa_buffer:
            attributes = vcsa_buffer.read(4)

        rows, cols, cursor_col, cursor_row = list(map(ord, struct.unpack('cccc', attributes)))
        cursor = (cursor_row, cursor_col) #, char_under_cursor.decode(encoding, 'ignore'))

        if buff == old_buff and cursor == old_cursor:
            time.sleep(2)
            continue

        log.debug(f"Cursor {cursor}")
        log.debug(f"Buff length {len(buff)}")
        log.debug(f"Rows, cols: {rows, cols}")

        write_buffer_to_screen(settings, old_buff, buff, old_cursor, cursor, character_encoding_width, settings.font, encoding, it8951_driver_program)

        old_buff = buff
        old_cursor = cursor


@click.command()
@click.option("--terminal-nr", help="Which /dev/tty to attach to..")
@click.option("--font-file", help="Path to a font-file.")
@click.option("--it8951-driver", help="Name of driver-executable.")
def main(terminal_nr, font_file, it8951_driver):
    settings = ConsoleSettings(
        rows=40,
        cols=80,
        font_file=font_file,
        font_height=16,
        font_width=8,
        screen_width=1200,
        screen_height=825,
    )

    main_loop(terminal_nr, settings, it8951_driver)

if __name__ == "__main__":
    main()
