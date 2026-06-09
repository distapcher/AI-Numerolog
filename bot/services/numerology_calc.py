from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PythagorasMatrix:
    day: int
    month: int
    year: int
    working_number: int
    second_number: int
    third_number: int
    fourth_number: int
    digit_counts: dict[int, int]

    @property
    def life_path_number(self) -> int:
        return _reduce_to_single(self.working_number, keep_master=True)

    @property
    def birth_day_number(self) -> int:
        return _reduce_to_single(self.day, keep_master=True)

    def cell_display(self, digit: int) -> str:
        count = self.digit_counts.get(digit, 0)
        if count == 0:
            return "—"
        return str(digit) * count

    def format_matrix(self) -> str:
        lines = [
            "Квадрат Пифагора (школа Александрова):",
            f"  {self.cell_display(1)} | {self.cell_display(4)} | {self.cell_display(7)}",
            f"  {self.cell_display(2)} | {self.cell_display(5)} | {self.cell_display(8)}",
            f"  {self.cell_display(3)} | {self.cell_display(6)} | {self.cell_display(9)}",
        ]
        return "\n".join(lines)

    def format_summary(self) -> str:
        counts = ", ".join(
            f"{d}: {self.digit_counts.get(d, 0)}" for d in range(1, 10)
        )
        return (
            f"Дата рождения: {self.day:02d}.{self.month:02d}.{self.year}\n"
            f"Рабочее число: {self.working_number}\n"
            f"Второе число: {self.second_number}\n"
            f"Третье число: {self.third_number}\n"
            f"Четвёртое число: {self.fourth_number}\n"
            f"Число жизненного пути: {self.life_path_number}\n"
            f"Число дня рождения: {self.birth_day_number}\n"
            f"Подсчёт цифр: {counts}\n\n"
            f"{self.format_matrix()}"
        )


def _sum_digits(n: int) -> int:
    return sum(int(ch) for ch in str(abs(n)))


def _reduce_to_single(n: int, *, keep_master: bool = False) -> int:
    while n > 9:
        if keep_master and n in (11, 22, 33):
            return n
        n = _sum_digits(n)
    return n


def parse_birth_date(text: str) -> tuple[int, int, int]:
    raw = (text or "").strip()
    match = re.fullmatch(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", raw)
    if not match:
        raise ValueError("Формат даты: <code>ДД.ММ.ГГГГ</code> (например 15.07.1985)")

    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
        raise ValueError("Проверьте корректность даты рождения.")
    return year, month, day


def calculate_pythagoras(day: int, month: int, year: int) -> PythagorasMatrix:
    """Классический квадрат Пифагора (русская школа Александрова)."""
    date_digits = [int(ch) for ch in f"{day:02d}{month:02d}{year}"]
    working = sum(date_digits)
    second = _sum_digits(working)

    day_str = str(day)
    first_day_digit = int(day_str[0])
    third = day - 2 * first_day_digit
    fourth = _sum_digits(third)

    all_digits: list[int] = []
    for value in (day, month, year, working, second, third, fourth):
        all_digits.extend(int(ch) for ch in str(abs(value)) if ch != "0")

    counts = {d: 0 for d in range(1, 10)}
    for digit in all_digits:
        if 1 <= digit <= 9:
            counts[digit] += 1

    return PythagorasMatrix(
        day=day,
        month=month,
        year=year,
        working_number=working,
        second_number=second,
        third_number=third,
        fourth_number=fourth,
        digit_counts=counts,
    )
