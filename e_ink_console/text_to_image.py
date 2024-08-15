import logging

import functools

from PIL import Image, ImageDraw

BLACK = 0
WHITE = 255

log = logging.getLogger(__name__)

def get_terminal_update_image(buffer_list, text_area, cursor, font, font_height, font_width, spacing=0):
    height = (text_area[2] - text_area[0] + 1)
    width = (text_area[3] - text_area[1] + 1)
    log.debug(f"Producing image with height, width {height, width} characters or {height*font_height, width*font_width} px")

    image = Image.new('1', (width * font_width, height * font_height), WHITE)
    draw = ImageDraw.Draw(image)
    for row in range(text_area[0], text_area[2] + 1):
        to_print = (buffer_list[row][text_area[1]:text_area[3] + 1])

        r = (row - text_area[0]) * font_height
        c = 0 * font_width
        log.debug(f"Printing @{r, c}: '{to_print}'")

        draw.text(
            (c, r),
            to_print,
            font=font,
            fill=BLACK,
            spacing=spacing,
        )

    r = cursor[0] - text_area[0]
    c = cursor[1] - text_area[1]
    pos = [
            ( c * font_width, (r + 0.9) * font_height),
            ((c + 1) * font_width, (r + 0.9) * font_height),
            ( c * font_width, (r + 1) * font_height),
            ((c + 1) * font_width, (r + 1) * font_height),
    ]
    draw.line(pos,
        fill=BLACK,
    )
    log.debug(f"Text area 0 {text_area[0]} and 1 is {text_area[1]}")
    log.debug(f"Printing cursor {cursor} @ {r, c }: {pos}.")

    return image

@functools.cache
def get_blank_image(screen_height, screen_width, background_color=WHITE):
    return Image.new('1', (screen_width, screen_height), background_color)


def identify_changed_text_area(old, new, rows, cols):
    """Locates the section of chaged characters on each line."""
    if len(old) != len(new):
        return [(i, 0, cols) for i in range(rows)]
    elif old == new:
        # To save some time
        return []

    diff_entries = []
    for row in range(rows):
        old_row_data = old[row * cols:(row + 1) * cols]
        new_row_data = new[row * cols:(row + 1) * cols]
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
        # Handle edge case of first drawing of console
        old_cursor_row = old_cursor[0] if old_cursor[0] >= 0 else new_cursor[0]
        old_cursor_col = old_cursor[1] if old_cursor[1] >= 0 else new_cursor[1]
        row_min = min(row_min, old_cursor_row, new_cursor[0])
        row_max = max(row_max, old_cursor_row, new_cursor[0])
        col_min = min(col_min, old_cursor_col, new_cursor[1])
        col_max = max(col_max, old_cursor_col, new_cursor[1])

    return (row_min, col_min, row_max, col_max)
