import logging

import os
import subprocess
import tempfile
import time

from enum import Enum
from pathlib import Path

from .text_to_image import (
    crop_image,
    get_contained_text_area,
    get_blank_image,
    get_full_terminal_image,
    identify_changed_text_area,
)

log = logging.getLogger(__name__)

_file_path = Path(os.path.realpath(__file__))
_repo_dir = _file_path.parent.absolute().parent.absolute()
DEBUG_BUFF_DIR = _repo_dir / Path("debug_buffer_images")

debug_buffer_no = 0


class ScreenUpdateMode(Enum):
    INIT = 0
    DU = 1
    GC16 = 2  # GC = grey scale
    GL16 = 3
    GLR16 = 4
    GLD16 = 5
    DU4 = 6
    A2 = 7  # Fast mode
    UNKNOWN1 = 8


def split(s, n):
    return [s[i : i + n] for i in range(0, len(s), n)]


def update_screen(
    screen_height,
    screen_width,
    image_file_path,
    pos_height,
    pos_width,
    program,
    mode=ScreenUpdateMode.GL16,
):
    cmd = [program, image_file_path, str(pos_width), str(pos_height), str(mode.value)]
    log.debug(f"Calling IT8951-drivers with arguments: {cmd}")

    process_output_file = tempfile.TemporaryFile()
    retries = 0
    total_retries = 3
    while retries < total_retries:
        try:
            subprocess.run(
                " ".join(cmd),
                shell=True,
                check=True,
                stdout=process_output_file,
                stderr=process_output_file,
            )
            return
        except subprocess.CalledProcessError:
            log.warning(
                f"Attempt {retries} out of {total_retries} to communicate with screen failed!"
            )
        finally:
            retries += 1
            time.sleep(1)

    process_output_file.seek(0)
    process_response = process_output_file.read()
    process_output_file.close()
    log.error(f"Failed to communicate with screen:\n{process_response.decode()}")


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


def write_buffer_to_screen(
    settings,
    old_buff,
    buff,
    old_cursor,
    cursor,
    character_encoding_width,
    it8951_driver,
    full_update=True,
    save_debugging_image=False,
):
    """Writes the buffer to the screen by decoding it, converting it to an image and sending it to the screen."""
    changed_sections = identify_changed_text_area(
        old_buff, buff, settings.rows, settings.cols
    )
    log.debug(f"changed_sections {changed_sections}")

    contained_text_area = get_contained_text_area(changed_sections, old_cursor, cursor)
    log.debug(f"contained_text_area {contained_text_area}")

    decoded_buff_list = split(
        buff.decode(settings.encoding, "replace"),
        settings.cols * character_encoding_width,
    )

    image = get_full_terminal_image(settings, decoded_buff_list, cursor)

    if full_update:
        log.debug("Doing a FULL update!")
        y_pos = 0
        x_pos = 0
        mode = ScreenUpdateMode.GC16
    else:
        image, x_pos, y_pos = crop_image(settings, image, contained_text_area)
        mode = ScreenUpdateMode.A2

    if save_debugging_image:
        global debug_buffer_no
        with open(f"{DEBUG_BUFF_DIR}/buffer_{debug_buffer_no}.png", "wb") as fb:
            image.save(fb)
            debug_buffer_no += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "buffer.png"), "wb") as fb:
            image.save(fb)

            update_screen(
                settings.screen_height,
                settings.screen_width,
                fb.name,
                y_pos,
                x_pos,
                it8951_driver,
                mode,
            )
