from PIL import Image, ImageDraw

BLACK = 0
WHITE = 255


def get_terminal_update_image(buffer_list, text_area, font, font_size, font_width):
    height = (text_area[1] - text_area[0] + 1)
    width = (text_area[3] - text_area[2] + 1)
    print(f"image height, width {height, width}")

    image = Image.new('1', (width * font_width, height * font_size), WHITE)
    draw = ImageDraw.Draw(image)
    for row in range(text_area[0], text_area[1] + 1):
        print(f"selecting print {row}, {text_area[2]} to {text_area[3] + 1}")
        to_print = (buffer_list[row][text_area[2]:text_area[3] + 1])
        r = row - text_area[0]
        c = 0
        print(f"drawing at {r, c}: '{to_print}'")
        draw.text(
            (c * font_size, r * font_size),
            to_print,
            font=font,
            fill=BLACK,
            spacing=2,
        )
    return image


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

    return (row_min, row_max, col_min, col_max)


def get_changed_buffer_text(buff, area):
    """Takes the buffer as a list of strings."""
    changed = []
    for row in buff[area[0]:area[1] + 1]:
        changed.append(row[area[2]:area[3] + 1])
    return changed
