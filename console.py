import os
import struct
import sys
import fcntl
import termios
import time

from dataclasses import dataclass
from PIL import ImageFont
from e_ink_console.text_to_image import get_contained_text_area, get_image, identify_changed_text_area

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

def main_loop(vcsa, tty):
    character_width = 1
    encoding = "utf-32"
    old_buff = b''

    while True:
        with open(vcsa, 'rb') as vcsa_buffer:
            with open(vcsa.replace("vcsa", "vcsu"), 'rb') as vcsu_buffer:
                attributes = vcsa_buffer.read(4)
                rows, cols, x, y = list(map(ord, struct.unpack('cccc', attributes)))

                buff = vcsu_buffer.read()
                nice_buff = ''.join([r.decode(encoding, 'replace') + '\n' for r in split(buff, cols * character_width)])
                char_under_cursor = buff[character_width * (y * rows + x):character_width * (y * rows + x + x)]
                cursor = (x, y, char_under_cursor.decode(encoding, 'ignore'))

                if buff != old_buff:
                    print("-----------")
                    print(nice_buff)
                    changed_sections = identify_changed_text_area(old_buff, buff, rows, cols)
                    # Create image with only updated portions
                    # Upload to screen
                old_buff = buff
                time.sleep(0.1)


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
    image = get_image(settings, "hej hej", font)

    with open("temp.jpg", "wb") as fb:
        image.save(fb)

    main_loop(vcsa, tty)
