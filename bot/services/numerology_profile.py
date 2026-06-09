from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from bot.services.numerology_calc import PythagorasMatrix, calculate_pythagoras, _reduce_to_single, _sum_digits

PYTHAGOREAN: dict[str, int] = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 6, "P": 7, "Q": 8, "R": 9,
    "S": 1, "T": 2, "U": 3, "V": 4, "W": 5, "X": 6, "Y": 7, "Z": 8,
    "А": 1, "Б": 2, "В": 3, "Г": 4, "Д": 5, "Е": 6, "Ё": 6, "Ж": 7, "З": 8,
    "И": 9, "Й": 1, "К": 2, "Л": 3, "М": 4, "Н": 5, "О": 6, "П": 7, "Р": 8,
    "С": 9, "Т": 1, "У": 2, "Ф": 3, "Х": 4, "Ц": 5, "Ч": 6, "Ш": 7, "Щ": 8,
    "Ъ": 9, "Ы": 1, "Ь": 2, "Э": 3, "Ю": 4, "Я": 5,
}

VOWELS = set("AEIOUYАЕЁИОУЫЭЮЯ")
KARMIC_DEBTS = {13, 14, 16, 19}
MASTER_NUMBERS = {11, 22, 33}


@dataclass(frozen=True)
class FullNumerologyProfile:
    name: str
    day: int
    month: int
    year: int
    matrix: PythagorasMatrix
    life_path: int
    birth_day: int
    soul_number: int
    destiny_expression: int
    power_fusion: int
    spiritual_awakening: int
    maturity: int
    karmic_debts: list[int]
    destiny_arcana: dict[str, int]
    karmic_tail_arcana: int
    master_numbers: list[int]
    challenges: dict[str, int]
    personal_year: int
    health_number: int
    money_code: dict[str, Any]
    compatibility_code: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "birth_date": f"{self.day:02d}.{self.month:02d}.{self.year}",
            "pythagoras_square": {
                "working_number": self.matrix.working_number,
                "second_number": self.matrix.second_number,
                "third_number": self.matrix.third_number,
                "fourth_number": self.matrix.fourth_number,
                "digit_counts": self.matrix.digit_counts,
                "matrix_text": self.matrix.format_matrix(),
            },
            "life_path_number": self.life_path,
            "birth_day_number": self.birth_day,
            "soul_number": self.soul_number,
            "destiny_expression_number": self.destiny_expression,
            "power_fusion_number": self.power_fusion,
            "spiritual_awakening_number": self.spiritual_awakening,
            "maturity_number": self.maturity,
            "karmic_debts": self.karmic_debts,
            "destiny_matrix_arcana": self.destiny_arcana,
            "karmic_tail_arcana": self.karmic_tail_arcana,
            "master_numbers": self.master_numbers,
            "challenge_numbers": self.challenges,
            "personal_year": self.personal_year,
            "health_number": self.health_number,
            "money_code": self.money_code,
            "compatibility_code": self.compatibility_code,
        }


def _letter_value(ch: str) -> int | None:
    return PYTHAGOREAN.get(ch.upper())


def _name_sum(name: str, *, vowels_only: bool = False, consonants_only: bool = False) -> int:
    total = 0
    for ch in name:
        val = _letter_value(ch)
        if val is None:
            continue
        is_vowel = ch.upper() in VOWELS
        if vowels_only and not is_vowel:
            continue
        if consonants_only and is_vowel:
            continue
        total += val
    return total


def _arcana(n: int) -> int:
    n = abs(n)
    while n > 22:
        n = _sum_digits(n)
    return n if n > 0 else 22


def _collect_karmic_debts(*values: int) -> list[int]:
    found: set[int] = set()

    def walk(n: int) -> None:
        n = abs(n)
        if n in KARMIC_DEBTS:
            found.add(n)
        if n > 9 and n not in MASTER_NUMBERS:
            walk(_sum_digits(n))

    for value in values:
        walk(value)
    return sorted(found)


def _collect_master_numbers(*values: int) -> list[int]:
    masters = {v for v in values if v in MASTER_NUMBERS}
    return sorted(masters)


def calculate_full_profile(
    *,
    name: str,
    day: int,
    month: int,
    year: int,
    current_year: int | None = None,
) -> FullNumerologyProfile:
    matrix = calculate_pythagoras(day, month, year)
    clean_name = name.strip() or "Гость"

    life_path = matrix.life_path_number
    birth_day = matrix.birth_day_number

    soul_raw = _name_sum(clean_name, vowels_only=True)
    soul_number = _reduce_to_single(soul_raw, keep_master=True)

    destiny_raw = _name_sum(clean_name)
    destiny_expression = _reduce_to_single(destiny_raw, keep_master=True)

    power_fusion = _reduce_to_single(soul_number + destiny_expression, keep_master=True)
    spiritual_awakening = _reduce_to_single(life_path + destiny_expression, keep_master=True)
    maturity = _reduce_to_single(life_path + destiny_expression, keep_master=True)

    year_sum = _sum_digits(year)
    month_reduced = _reduce_to_single(month, keep_master=True)
    day_reduced = _reduce_to_single(day, keep_master=True)
    year_reduced = _reduce_to_single(year_sum, keep_master=True)

    a1 = _arcana(month)
    a2 = _arcana(day)
    a3 = _arcana(day + month)
    a4 = _arcana(year_sum)
    a5 = _arcana(a1 + a2)
    a6 = _arcana(a3 + a4)
    a7 = _arcana(a5 + a6)
    a8 = _arcana(a1 + a2 + a3 + a4 + a5 + a6 + a7)

    destiny_arcana = {
        "arcana_1_month_comfort": a1,
        "arcana_2_day_talent": a2,
        "arcana_3_current_task": a3,
        "arcana_4_karmic_tail": a4,
        "arcana_5_social_mission": a5,
        "arcana_6_growth_points": a6,
        "arcana_7_genius_zone": a7,
        "arcana_8_total_incarnation_task": a8,
    }

    ch1 = abs(day_reduced - month_reduced)
    ch2 = abs(day_reduced - year_reduced)
    ch3 = abs(ch1 - ch2)
    challenges = {
        "challenge_1": ch1,
        "challenge_2": ch2,
        "challenge_3": ch3,
    }

    cy = current_year or date.today().year
    personal_year = _reduce_to_single(day + month + cy, keep_master=True)

    counts = matrix.digit_counts
    health_raw = (
        counts.get(4, 0) * 4
        + counts.get(5, 0) * 5
        + counts.get(6, 0) * 6
    )
    health_number = _reduce_to_single(health_raw or day_reduced, keep_master=True)

    eights_in_name = sum(1 for ch in clean_name if _letter_value(ch) == 8)
    money_code = {
        "matrix_digits_4_5_6_8": {
            "4": counts.get(4, 0),
            "5": counts.get(5, 0),
            "6": counts.get(6, 0),
            "8": counts.get(8, 0),
        },
        "money_line_strength": counts.get(4, 0) + counts.get(5, 0) + counts.get(6, 0),
        "eights_in_name": eights_in_name,
        "destiny_matrix_arcana_8": a8,
    }

    compatibility_code = _reduce_to_single(life_path + soul_number, keep_master=True)

    karmic_debts = _collect_karmic_debts(
        matrix.working_number,
        soul_raw,
        destiny_raw,
        day,
        month,
        year_sum,
    )
    master_numbers = _collect_master_numbers(
        life_path,
        birth_day,
        soul_number,
        destiny_expression,
        power_fusion,
        spiritual_awakening,
        maturity,
        personal_year,
    )

    return FullNumerologyProfile(
        name=clean_name,
        day=day,
        month=month,
        year=year,
        matrix=matrix,
        life_path=life_path,
        birth_day=birth_day,
        soul_number=soul_number,
        destiny_expression=destiny_expression,
        power_fusion=power_fusion,
        spiritual_awakening=spiritual_awakening,
        maturity=maturity,
        karmic_debts=karmic_debts,
        destiny_arcana=destiny_arcana,
        karmic_tail_arcana=a4,
        master_numbers=master_numbers,
        challenges=challenges,
        personal_year=personal_year,
        health_number=health_number,
        money_code=money_code,
        compatibility_code=compatibility_code,
    )


def format_profile_for_ai(profile: FullNumerologyProfile) -> str:
    arc = profile.destiny_arcana
    money = profile.money_code
    lines = [
        f"Имя: {profile.name}",
        f"Дата рождения: {profile.day:02d}.{profile.month:02d}.{profile.year}",
        "",
        "=== КВАДРАТ ПИФАГОРА ===",
        profile.matrix.format_summary(),
        "",
        "=== ОСНОВНЫЕ ЧИСЛА ===",
        f"1. Число Жизненного Пути (ЧЖП): {profile.life_path}",
        f"2. Число Дня Рождения (ЧДР): {profile.birth_day}",
        f"3. Число Души: {profile.soul_number}",
        f"4. Число Судьбы (Экспрессии): {profile.destiny_expression}",
        f"5. Число Силы (Слияния): {profile.power_fusion}",
        f"6. Число Духовного Пробуждения: {profile.spiritual_awakening}",
        f"7. Число Зрелости: {profile.maturity}",
        f"8. Кармические долги (13, 14, 16, 19): {profile.karmic_debts or 'не обнаружены'}",
        f"9. Кармический хвост (4-й аркан Матрицы Судьбы): {profile.karmic_tail_arcana}",
        f"10. Управляющие числа (11, 22, 33): {profile.master_numbers or 'нет'}",
        "",
        "=== АРКАНЫ МАТРИЦЫ СУДЬБЫ (1–22) ===",
        f"1-й аркан (месяц, энергия комфорта): {arc['arcana_1_month_comfort']}",
        f"2-й аркан (день, талант): {arc['arcana_2_day_talent']}",
        f"3-й аркан (день+месяц, задача сейчас): {arc['arcana_3_current_task']}",
        f"4-й аркан (год, кармический хвост): {arc['arcana_4_karmic_tail']}",
        f"5-й аркан (1+2, социальная миссия): {arc['arcana_5_social_mission']}",
        f"6-й аркан (3+4, точки роста): {arc['arcana_6_growth_points']}",
        f"7-й аркан (5+6, зона гениальности): {arc['arcana_7_genius_zone']}",
        f"8-й аркан (тотальная задача воплощения): {arc['arcana_8_total_incarnation_task']}",
        "",
        "=== ЧИСЛА ИСПЫТАНИЙ ===",
        f"1-е испытание (|день − месяц|): {profile.challenges['challenge_1']}",
        f"2-е испытание (|день − год|): {profile.challenges['challenge_2']}",
        f"3-е испытание (|1-е − 2-е|): {profile.challenges['challenge_3']}",
        "",
        f"15. Личный год на {date.today().year}: {profile.personal_year}",
        f"16. Число Здоровья: {profile.health_number}",
        "",
        "=== ДЕНЕЖНЫЙ КОД ===",
        f"Цифры 4-5-6-8 в психоматрице: {money['matrix_digits_4_5_6_8']}",
        f"Сила денежной линии (4+5+6): {money['money_line_strength']}",
        f"Восьмёрки в имени: {money['eights_in_name']}",
        f"8-й аркан Матрицы Судьбы: {money['destiny_matrix_arcana_8']}",
        "",
        f"18. Код совместимости (личная вибрация): {profile.compatibility_code}",
        "(Полный расчёт совместимости требует данных партнёра.)",
    ]
    return "\n".join(lines)
