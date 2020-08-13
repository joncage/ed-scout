from EDScoutWebUI.HudColourAdjuster import *


def test_can_read_values_correctly():
    data_file = "TestData\\example.xml"
    matrix_values = get_matrix_values(data_file)
    assert matrix_values is not None
    assert matrix_values['MatrixRed'] == [1, 0, 0]
    assert matrix_values['MatrixGreen'] == [0, 1, 0]
    assert matrix_values['MatrixBlue'] == [0, 0, 1]
