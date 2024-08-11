import os
import struct
import sys
import fcntl
import termios
import time

from dataclasses import dataclass
from PIL import ImageFont
from e_ink_console.text_to_image import (
    get_changed_buffer_text,
    get_contained_text_area,
    get_terminal_update_image,
    identify_changed_text_area,
)

@dataclass
class ConsoleSettings():
    rows: int
    cols: int
    font_path: str
    font_size: int = 16


def split(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]

def setup(settings, tty):
    # Check valid vcsa
    try:
        os.stat(vcsa)
        os.stat(tty)
    except OSError:
        print("Error with {vcsa} or {tty}.")
        exit(1)

    # Set size
    size = struct.pack("HHHH", settings.rows, settings.cols, 0, 0)
    with open(tty, 'w') as file_buffer:
        fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)

def main_loop(vcsa, tty, font, font_size):
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
            print("skipping update")
            continue

        print(f"cursor {cursor}")
        changed_sections = identify_changed_text_area(old_buff, buff, rows, cols)
        print(f"changed_sections {changed_sections}")
        contained_text_area = get_contained_text_area(changed_sections, old_cursor, cursor)
        print(f"contained_text_area {contained_text_area}")

        decoded_buff_list = split(buff.decode(encoding, "replace"), cols * character_encoding_width)
        changed_text = get_changed_buffer_text(decoded_buff_list, contained_text_area)

# crashes the get_image:
# contained_text_area (17, 18, 0, 1)
        image = get_terminal_update_image(
            changed_text,
            contained_text_area[1] - contained_text_area[0] + 1,
            contained_text_area[3] - contained_text_area[2] + 1,
            font,
            font_size,
        )
        with open("buff.png", "wb") as fb:
            image.save(fb)

        old_buff = buff
        old_cursor = cursor

        # Upload to screen
        nice = "\n".join(decoded_buff_list)
        print(nice)
        print(f"----------- buff length {len(buff)} (nice {len(nice)})")
        print(f"----------- row, col: {rows, cols}")


if __name__ == "__main__":
    vcsa = "/dev/vcsa" + sys.argv[1]
    tty = "/dev/tty" + sys.argv[1]
    settings = ConsoleSettings(
        rows=20,
        cols=40,
        font_path=sys.argv[2],
        font_size=16,
    )
    setup(settings, tty)

    font = ImageFont.truetype(settings.font_path, settings.font_size)

    main_loop(vcsa, tty, font, settings.font_size)
