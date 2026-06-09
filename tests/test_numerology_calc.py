from bot.services.numerology_calc import calculate_pythagoras


def test_pythagoras_square_02_05_1983() -> None:
    matrix = calculate_pythagoras(2, 5, 1983)

    assert matrix.working_number == 28
    assert matrix.second_number == 10
    assert matrix.third_number == 24
    assert matrix.fourth_number == 6
    assert matrix.digit_counts == {
        1: 2,
        2: 3,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 0,
        8: 2,
        9: 1,
    }
    assert matrix.format_matrix() == (
        "Квадрат Пифагора (школа Александрова):\n"
        "  11 | 4 | —\n"
        "  222 | 5 | 88\n"
        "  3 | 6 | 9"
    )


def test_pythagoras_square_25_01_1998() -> None:
    matrix = calculate_pythagoras(25, 1, 1998)

    assert matrix.working_number == 35
    assert matrix.third_number == 31
    assert matrix.fourth_number == 4
