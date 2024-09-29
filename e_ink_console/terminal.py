import logging

import fcntl
import os
import struct
import termios
import time

from PIL import Image, ImageFont

from e_ink_console.screen import write_buffer_to_screen

log = logging.getLogger()


class TerminalSettings:
    def __init__(
        self,
        tty: str,
        vcsa: str,
        screen_width: int,
        screen_height: int,
        font_file: str,
        font_size: int,
        encoding: str = "utf-8",
        rows: int = 0,
        cols: int = 0,
        full_update_interval=10,
    ):
        self.tty = tty
        self.vcsa = vcsa
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_file = font_file
        self.font_size = font_size
        self.encoding = encoding
        self.full_update_interval = full_update_interval

        self.verify_settings()
        self.update_settings(rows, cols)

    def verify_settings(self):
        try:
            os.stat(self.tty)
        except OSError:
            OSError("Error with or {self.tty}.")
        try:
            os.stat(self.vcsa)
        except OSError:
            OSError("Error with {self.vcsa}.")

    def update_settings(self, rows, cols):
        self.font = ImageFont.truetype(self.font_file, self.font_size)
        # Make an estimation of the font-width (as int) that on the large side.
        # We don't want to accidentally write outside the scren.
        self.font_width = int(self.font.getlength("1234567890") // 10) + 1
        self.font_height = sum(self.font.getmetrics())
        log.info(
            f"Setting font width and height to: {self.font_width}, {self.font_height}"
        )

        self.rows = rows or int(self.screen_height / self.font_height)
        self.cols = cols or int(self.screen_width / self.font_width)
        log.info(
            f"Calculated number of rows to {self.rows}  and number of columns to {self.cols}."
        )

        residual_height_margin = self.screen_height - self.rows * self.font_height
        residual_width_margin = self.screen_width - self.cols * self.font_width
        self.residual_margins = (residual_height_margin, residual_width_margin)
        log.info(
            f"Residual pixels in height is {self.residual_margins[0]} and width is {self.residual_margins[1]}"
        )

        # Define the cursor here so we don't need to recreate it with every draw
        self.cursor_thickness = int(round(0.1 * self.font_height)) or 1
        self.cursor_image = Image.new(
            "1",
            (self.font_width, self.cursor_thickness),
            0,
        )
        log.debug(
            f"Cursor dimensions are set to {self.cursor_thickness} x {self.font_width}."
        )

        try:
            size = struct.pack("HHHH", self.rows, self.cols, 0, 0)
            with open(self.tty, "wb") as file_buffer:
                fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)
        except OSError as e:
            log.critical(f"Could not set terminal size: {e}. Using default values.")
            self.rows = 20
            self.cols = 80


class DummyHandler:
    def terminated(self):
        return False


def read_terminal_properties(settings):
    with open(settings.vcsa, "rb") as vcsa_buffer:
        attributes = vcsa_buffer.read(4)

    return list(map(ord, struct.unpack("cccc", attributes)))


def main_loop(settings, it8951_driver_program, linux_process_handler=DummyHandler()):
    character_encoding_width = 1
    old_buff = b""
    _, _, cursor_col, cursor_row = read_terminal_properties(settings)
    old_cursor = (cursor_row, cursor_col)

    last_full_update = time.time()
    while not linux_process_handler.terminated:
        with open(settings.vcsa.replace("vcsa", "vcs"), "rb") as vcsu_buffer:
            buff = vcsu_buffer.read()

        rows, cols, cursor_col, cursor_row = read_terminal_properties(settings)
        cursor = (cursor_row, cursor_col)

        if buff == old_buff and cursor == old_cursor:
            time.sleep(0.1)
            continue

        log.debug(f"Cursor {cursor}, old cursor {old_cursor}.")
        log.debug(f"Buff length {len(buff)}")
        log.debug(f"Rows, cols: {rows, cols}")

        now = time.time()
        if (now - last_full_update) > settings.full_update_interval:
            full_update = True
            last_full_update = now
        else:
            full_update = False

        write_buffer_to_screen(
            settings,
            old_buff,
            buff,
            old_cursor,
            cursor,
            character_encoding_width,
            it8951_driver_program,
            full_update,
        )

        old_buff = buff
        old_cursor = cursor
