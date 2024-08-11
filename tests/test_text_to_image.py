import pytest
from e_ink_console.text_to_image import identify_changed_text_area


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


