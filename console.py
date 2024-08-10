import os
import struct
import sys
import fcntl
import termios
import time

from PIL import ImageFont
from text_to_image import get_image


def split(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]

def setup(tty, font_path, font_size, rows, cols):
    # Check valid vcsa
    try:
        os.stat(vcsa)
        os.stat(tty)
    except OSError:
        print("Error with {vcsa} or {tty}.")
        exit(1)
    font = ImageFont.truetype(font_path, font_size)

    # Set size
    size = struct.pack("HHHH", rows, cols, 0, 0)
    with open(tty, 'w') as file_buffer:
        fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)

    return font

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
                old_buff = buff
                time.sleep(0.1)

if __name__ == "__main__":
    vcsa = "/dev/vcsa" + sys.argv[1]
    tty = "/dev/tty" + sys.argv[1]
    font_path = sys.argv[2]
    font_size = 16
    rows = 5
    cols = 40
    font = setup(tty, font_path, font_size=font_size, rows=rows, cols=cols)
    image = get_image(rows, cols, font, "hej hej", font_size)

    with open("temp.jpg", "wb") as fb:
        image.save(fb)

    main_loop(vcsa, tty)
