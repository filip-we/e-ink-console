import logging

import functools

from PIL import Image, ImageDraw

BLACK = 0
WHITE = 255

log = logging.getLogger(__name__)


def get_full_terminal_image(settings, buffer_list, cursor, spacing=0):
    width = settings.cols * settings.font_width
    height = settings.rows * settings.font_height
    image = Image.new("1", (width, height), WHITE)
    log.debug(f"Creating image with dimensions {width} x {height}.")

    draw = ImageDraw.Draw(image)
    for row in range(settings.rows):
        draw.text(
            (0, row * settings.font_height),
            buffer_list[row],
            font=settings.font,
            fill=BLACK,
            spacing=spacing,
        )
    cursor_height = int(settings.font_height * 0.9)
    image.paste(
        settings.cursor_image,
        (
            cursor[1] * settings.font_width,
            (cursor[0] + settings.cursor_thickness - 1) * cursor_height,
        ),
    )

    return image


def get_partial_terminal_image(settings, buffer_list, text_area, cursor, spacing=0):
    height = text_area[2] - text_area[0] + 1
    width = text_area[3] - text_area[1] + 1
    log.debug(
        f"Producing image with height, width {height, width} characters or {height*settings.font_height, width*settings.font_width} px"
    )

    image = Image.new(
        "1", (width * settings.font_width, height * settings.font_height), WHITE
    )
    draw = ImageDraw.Draw(image)
    for row in range(text_area[0], text_area[2] + 1):
        to_print = buffer_list[row][text_area[1] : text_area[3] + 1]

        r = (row - text_area[0]) * settings.font_height
        c = 0 * settings.font_width

        draw.text(
            (c, r),
            to_print,
            font=settings.font,
            fill=BLACK,
            spacing=spacing,
        )

    image.paste(
        settings.cursor_image,
        (
            (cursor[1] - text_area[1]) * settings.font_width,
            ((cursor[0] - text_area[0]) + settings.cursor_thickness - 1)
            * settings.font_height,
        ),
    )

    return image


@functools.cache
def get_blank_image(screen_height, screen_width, background_color=WHITE):
    return Image.new("1", (screen_width, screen_height), background_color)


def identify_changed_text_area(old, new, rows, cols):
    """Locates the section of chaged characters on each line."""
    if len(old) != len(new):
        return [(i, 0, cols) for i in range(rows)]
    elif old == new:
        # To save some time
        return []

    diff_entries = []
    for row in range(rows):
        old_row_data = old[row * cols : (row + 1) * cols]
        new_row_data = new[row * cols : (row + 1) * cols]
        diff = [x == y for x, y in zip(old_row_data, new_row_data)]
        try:
            first_diff = diff.index(False)
        except ValueError:
            continue
        diff.reverse()
        try:
            last_diff = cols - 1 - diff.index(False)
        except ValueError:
            diff_entries.append((row, first_diff, first_diff))
        diff_entries.append((row, first_diff, last_diff))
    return diff_entries


def get_contained_text_area(row_sections, old_cursor, new_cursor):
    """This draws a box around all sections given as input."""
    row_min = 9999
    row_max = -1
    col_min = 9999
    col_max = -1

    for section in row_sections:
        row_min = min(row_min, section[0])
        row_max = max(row_max, section[0])
        col_min = min(col_min, section[1])
        col_max = max(col_max, section[2])

    if old_cursor != new_cursor:
        row_min = min(row_min, old_cursor[0], new_cursor[0])
        row_max = max(row_max, old_cursor[0], new_cursor[0])
        col_min = min(col_min, old_cursor[1], new_cursor[1])
        col_max = max(col_max, old_cursor[1], new_cursor[1])

    return (row_min, col_min, row_max, col_max)


def crop_image(settings, image, text_area):
    """Takes a PIL-image and returns a cropped image on the section described in text_area. text_area is given in rows and columns."""
    # Order of points:
    # Top horizontal, left vertical, bottom horizontal, right vertical
    points = [
        max(text_area[1] * settings.font_width - 10, 0),
        max(text_area[0] * settings.font_height - 10, 0),
        min((text_area[3] + 1), settings.cols) * settings.font_width,
        min((text_area[2] + 1), settings.rows) * settings.font_height,
    ]
    log.debug(f"Cropping image to corners {points[0:1]} and {points[2:3]}.")
    image = image.resize(
        size=[points[2] - points[0], points[3] - points[1]],
        box=points,
    )
    return image, points[0], points[1]
