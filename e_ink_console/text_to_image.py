from PIL import Image, ImageDraw

BLACK = 0
WHITE = 255

def get_image(settings, text, font):
    # Create image in black and white with 1 bit per pixel.
    image = Image.new('1', (settings.cols * settings.font_size, settings.rows * settings.font_size), WHITE) # probably white
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=BLACK, spacing=2)
    return image

def identify_changed_text_area(old, new, rows, cols):
    """Locates the section of chaged characters on each line."""
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
