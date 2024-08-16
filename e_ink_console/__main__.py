import logging

import click
import os
import struct
import sys

from e_ink_console.screen import clear_screen
from e_ink_console.terminal import TerminalSettings, main_loop

log = logging.getLogger()
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(ch)


def assert_console_input_file_params(files):
    for name, path in files.items():
        try:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Could not locate {name} '{path}'.")
        except TypeError:
            raise FileNotFoundError(f"Could not locate {name} '{path}'.")


@click.command()
@click.option("--terminal-nr", help="Which /dev/tty to attach to..")
@click.option("--font-file", help="Path to a font-file.")
@click.option("--font-size", help="Size of font, in pixles.", default=16)
@click.option("--it8951-driver", help="Name of driver-executable.")
@click.option("--rows", default=0)
@click.option("--cols", default=0)
def main(terminal_nr, font_file, font_size, it8951_driver, rows, cols):
    assert terminal_nr

    assert_console_input_file_params(
        {
            "Font-file": font_file,
            "IT8951-driver-file": it8951_driver,
        }
    )

    settings = TerminalSettings(
        tty=f"/dev/tty{terminal_nr}",
        vcsa=f"/dev/vcsa{terminal_nr}",
        rows=rows,
        cols=cols,
        font_file=font_file,
        font_size=font_size,
        screen_width=1200,
        screen_height=825,
    )

    clear_screen(settings.screen_height, settings.screen_width, it8951_driver)

    main_loop(settings, it8951_driver)

main()
