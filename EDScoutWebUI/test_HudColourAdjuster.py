from . import HudColourAdjuster
import os


def get_test_file_path(filename):
    script_path = os.path.dirname(__file__)
    data_dir = "./TestData/"
    return os.path.abspath(os.path.join(script_path, data_dir, filename))


def test_can_read_values_correctly():

    script_path = os.path.dirname(__file__)
    data_file = get_test_file_path("example.xml")
    data_path = os.path.join(script_path, data_file)
    matrix_values = HudColourAdjuster.get_matrix_values(data_path)
    assert matrix_values is not None
    assert matrix_values['MatrixRed'] == [1, 0, 0]
    assert matrix_values['MatrixGreen'] == [0, 1, 0]
    assert matrix_values['MatrixBlue'] == [0, 0, 1]


def test_colour_conversion_with_identity_does_no_change_colours():
    colour_matrix = {
        'MatrixRed': [1, 0, 0],
        'MatrixGreen': [0, 1, 0],
        'MatrixBlue': [0, 0, 1],
    }

    original_colour = [0.5, 0.5, 0.5]

    new_colour = HudColourAdjuster.adjust_colours(original_colour, colour_matrix)

    assert new_colour == [0.5, 0.5, 0.5]


def test_colour_conversion_make_red_green():
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    original_colour = [0.5, 0.5, 0.5]

    new_colour = HudColourAdjuster.adjust_colours(original_colour, colour_matrix)

    assert new_colour == [0.0, 1.0, 0.5]


def test_colour_conversion_make_red_green_as_hex():
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    original_colour = "#808080"

    new_colour = HudColourAdjuster.hex_colour_shift(original_colour, colour_matrix)

    assert new_colour == "#00FF80"


def test_css_conversion_values_are_replaced(monkeypatch):
    original_data = ".charted { color: #9f9f9f; background: #333333; }"
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    def mock_hex_colour_shift(original_data, colour_matrix):
        return '#123456'

    monkeypatch.setattr(HudColourAdjuster, "hex_colour_shift", mock_hex_colour_shift)

    converted = HudColourAdjuster.remap_styles(original_data, colour_matrix)

    assert converted == ".charted { color: #123456; background: #123456; }"


def test_css_conversion_values_are_set_crrectly(monkeypatch):
    original_data = ".charted { color: #FF0000; background: #00FFFF; }"
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],  # Shift red to green
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    converted = HudColourAdjuster.remap_styles(original_data, colour_matrix)

    assert converted == ".charted { color: #00FF00; background: #00FFFF; }"
