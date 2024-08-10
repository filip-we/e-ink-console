from PIL import Image, ImageDraw


def get_image(rows, cols, font, text, font_size):
    image = Image.new('1', (rows * font_size, cols * font_size), 255) # probably white
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=0, spacing=2)
    return image
