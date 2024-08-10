import os
import struct
import sys
import fcntl
import termios
import time



vcsa = "/dev/vcsa" + sys.argv[1]
tty = "/dev/tty" + sys.argv[1]

rows = 5
cols = 40

def split(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]

# Check valid vcsa
try:
    os.stat(vcsa)
    os.stat(tty)
except OSError:
    print("Error with {vcsa} or {tty}.")
    exit(1)

# Set size
size = struct.pack("HHHH", rows, cols, 0, 0)
with open(tty, 'w') as file_buffer:
    fcntl.ioctl(file_buffer.fileno(), termios.TIOCSWINSZ, size)

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

