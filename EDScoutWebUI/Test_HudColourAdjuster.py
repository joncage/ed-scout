from EDScoutWebUI.HudColourAdjuster import *


def test_can_read_values_correctly():
    data_file = "TestData\\example.xml"
    matrix_values = get_matrix_values(data_file)
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

    new_colour = adjust_colours(original_colour, colour_matrix)

    assert new_colour == [0.5, 0.5, 0.5]



def test_colour_conversion_make_red_green():
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    original_colour = [0.5, 0.5, 0.5]

    new_colour = adjust_colours(original_colour, colour_matrix)

    assert new_colour == [0.0, 1.0, 0.5]

def test_colour_conversion_make_red_green_as_hex():
    colour_matrix = {
        'MatrixRed': [0.0, 1.0, 0.0],
        'MatrixGreen': [0.0, 1.0, 0.0],
        'MatrixBlue': [0.0, 0.0, 1.0],
    }

    original_colour = "#808080"


    new_colour = hex_colour_shift(original_colour, colour_matrix)

    assert new_colour == "#00FF80"
