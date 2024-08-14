import pytest
from e_ink_console.text_to_image import get_contained_text_area, identify_changed_text_area

from console import ConsoleSettings, main_loop

@pytest.mark.parametrize(
    "old,new,changed",
    [
        ["1234abcd1234", "1234abcd1234", []],
        ["1234abcd1234", "1234ab  1234", [(1, 2, 3)]],
        ["1234abcd1234", " 234ab  1234", [(0, 0, 0), (1, 2, 3)]],
        ["1234abcd1234", " 234ab  12 4", [(0, 0, 0), (1, 2, 3), (2, 2, 2)]],
    ],
)
def test_identify_changed_text_area(old, new, changed):
    actual = identify_changed_text_area(old, new, rows=3, cols=4)
    assert actual == changed

@pytest.mark.parametrize(
    "sections,expected",
    [
        [[(1, 2, 3)], (1, 2, 1, 3)],
        [[(0, 0, 0), (1, 2, 3)], (0, 0, 1, 3)],
        [[(0, 0, 0), (1, 2, 3), (2, 2, 2)], (0, 0, 2, 3)],
    ],
)
def test_get_contained_text_area(sections, expected):
    actual = get_contained_text_area(sections, (0,0), (0,0))
    assert actual == expected


def test_terminal(terminal_nr, it8951_driver, font_file):
    rows = 80
    cols = 40
    settings = ConsoleSettings(
        rows=rows,
        cols=cols,
        font_file=font_file,
        font_height=16,
        font_width=8,
        screen_width=1200,
        screen_height=825,
    )


    #clear_screen(settings.screen_height, settings.screen_width, it8951_driver)
    with open("/dev/tty{terminal_nr}", "wb") as fb:
        fb.write("Hej hej hej".encode("utf-8"))

    main_loop(terminal_nr, settings, it8951_driver)

0
