import logging

import os
import subprocess
import tempfile

from .text_to_image import (
    get_contained_text_area,
    get_blank_image,
    get_terminal_update_image,
    identify_changed_text_area,
)
log = logging.getLogger(__name__)


def split(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]

def update_screen(screen_height, screen_width, image_file_path, pos_height, pos_width, program):
    cmd = [program, image_file_path, str(pos_width), str(pos_height)]
    log.debug(f"Calling IT8951-drivers with arguments: {cmd}")
    p = subprocess.run(" ".join(cmd),
        shell=True,
        check=True,
    )

def clear_screen(screen_height, screen_width, it8951_driver):
    image = get_blank_image(screen_height, screen_width)
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "background.png"), "wb") as fb:
            image.save(fb)
            update_screen(
                screen_height,
                screen_width,
                fb.name,
                0,
                0,
                it8951_driver,
            )

def write_buffer_to_screen(settings, old_buff, buff, old_cursor, cursor, character_encoding_width, it8951_driver):
    """Writes the buffer to the screen by decoding it, converting it to an image and sending it to the screen."""
    changed_sections = identify_changed_text_area(old_buff, buff, settings.rows, settings.cols)
    log.debug(f"changed_sections {changed_sections}")

    contained_text_area = get_contained_text_area(changed_sections, old_cursor, cursor)
    log.debug(f"contained_text_area {contained_text_area}")

    decoded_buff_list = split(buff.decode(settings.encoding, "replace"), settings.cols * character_encoding_width)

    image = get_terminal_update_image(
        settings,
        decoded_buff_list,
        contained_text_area,
        cursor,
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "buffer.png"), "wb") as fb:
            image.save(fb)
            update_screen(
                settings.screen_height,
                settings.screen_width,
                fb.name,
                contained_text_area[0] * settings.font_height,
                contained_text_area[1] * settings.font_width,
                    it8951_driver,
                )
