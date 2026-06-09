from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from bot.config import Settings
from bot.services.numerology_calc import calculate_pythagoras

logger = logging.getLogger(__name__)

# Эндпоинты the-numerology-api (RapidAPI). Психоматрицы на Rapid нет —
# квадрат Пифагора считается локально (школа Александрова).
RAPID_NUMEROLOGY_ENDPOINTS: tuple[str, ...] = (
    "life_path",
    "attitude_number",
    "challenge_number",
    "karmic_debt",
    "karmic_lessons",
    "destiny_number",
    "heart_desire",
    "personality_number",
    "personal_year",
    "period_cycles",
    "lucky_numbers",
    "balance_number",
    "subconscious_number",
    "thought_number",
)


class NumerologyApiError(Exception):
    pass


@dataclass(frozen=True)
class NameParts:
    first_name: str
    middle_name: str
    last_name: str
    full_name: str
    initials: str


@dataclass(frozen=True)
class NumerologyProfile:
    matrix_text: str
    summary_text: str


def split_full_name(full_name: str) -> NameParts:
    parts = [p for p in full_name.split() if p]
    if not parts:
        first, middle, last = "Guest", "", "Guest"
    elif len(parts) == 1:
        first, middle, last = parts[0], "", parts[0]
    elif len(parts) == 2:
        first, middle, last = parts[0], "", parts[1]
    else:
        first, middle, last = parts[0], " ".join(parts[1:-1]), parts[-1]

    initials = "".join(part[0].upper() for part in (first, middle, last) if part) or "X"
    return NameParts(
        first_name=first,
        middle_name=middle,
        last_name=last,
        full_name=" ".join(parts) if parts else "Guest",
        initials=initials,
    )


def _format_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "да" if value else "нет"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        items = [_format_scalar(item) for item in value]
        return "; ".join(item for item in items if item)
    if isinstance(value, dict):
        return _format_dict(value)
    return str(value)


def _format_dict(data: dict[str, Any], *, indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            nested = _format_dict(value, indent=indent + 1)
            if nested:
                lines.append(nested)
            continue
        text = _format_scalar(value)
        if text:
            lines.append(f"{prefix}{key}: {text}")
    return "\n".join(lines)


ENDPOINT_LABELS: dict[str, str] = {
    "life_path": "Число жизненного пути (Life Path)",
    "attitude_number": "Число отношения / Солнца (Attitude)",
    "challenge_number": "Числа испытаний (Challenge)",
    "karmic_debt": "Кармический долг (Karmic Debt)",
    "karmic_lessons": "Кармические уроки (Karmic Lessons)",
    "destiny_number": "Число судьбы / экспрессии (Destiny)",
    "heart_desire": "Число души (Heart's Desire / Soul Urge)",
    "personality_number": "Число личности (Personality)",
    "personal_year": "Личный год (Personal Year)",
    "period_cycles": "Жизненные периоды (Period Cycles)",
    "lucky_numbers": "Счастливые числа (Lucky Numbers)",
    "balance_number": "Число баланса (Balance)",
    "subconscious_number": "Число подсознания (Subconscious Self)",
    "thought_number": "Число рациональной мысли (Rational Thought)",
}


class NumerologyApiClient:
    """Нумерология через RapidAPI the-numerology-api + локальный квадрат Пифагора."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "x-rapidapi-key": settings.rapidapi_key,
            "x-rapidapi-host": settings.rapidapi_host,
            "Content-Type": "application/json",
        }
        self._base_url = f"https://{settings.rapidapi_host}"

    def _endpoint_params(
        self,
        endpoint: str,
        *,
        name: NameParts,
        day: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        dob = f"{year:04d}-{month:02d}-{day:02d}"
        birth = {
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
        }
        if endpoint in {"life_path", "attitude_number", "challenge_number", "karmic_debt", "period_cycles"}:
            return birth
        if endpoint == "personal_year":
            return {
                **birth,
                "prediction_year": date.today().year,
            }
        if endpoint in {"destiny_number", "heart_desire", "personality_number"}:
            return {
                "first_name": name.first_name,
                "middle_name": name.middle_name or name.first_name,
                "last_name": name.last_name,
            }
        if endpoint == "karmic_lessons":
            return {"full_name": name.full_name}
        if endpoint == "lucky_numbers":
            return {"birthdate": dob, "full_name": name.full_name}
        if endpoint == "balance_number":
            return {"initials": name.initials}
        if endpoint == "subconscious_number":
            return {"name": name.full_name}
        if endpoint == "thought_number":
            return {"first_name": name.first_name, "birth_day": day}
        raise ValueError(f"Unknown endpoint: {endpoint}")

    async def _rapidapi_get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
        url = f"{self._base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=self._headers, params=params)
        except httpx.HTTPError as exc:
            logger.warning("RapidAPI GET %s network error: %s", endpoint, exc)
            return None

        if response.status_code >= 400:
            logger.warning(
                "RapidAPI GET %s -> %s: %s",
                endpoint,
                response.status_code,
                response.text[:300],
            )
            return None

        try:
            data = response.json()
        except ValueError:
            return None

        if not isinstance(data, dict):
            return None

        message = data.get("message")
        if isinstance(message, str):
            lowered = message.lower()
            if "disabled for your subscription" in lowered:
                logger.info("RapidAPI %s skipped: subscription tier", endpoint)
                return None
            if "missing required" in lowered or "does not exist" in lowered:
                logger.warning("RapidAPI %s: %s", endpoint, message)
                return None

        return data

    async def _fetch_endpoint(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> tuple[str, dict[str, Any] | None]:
        return endpoint, await self._rapidapi_get(endpoint, params)

    def _format_endpoint_block(self, endpoint: str, data: dict[str, Any]) -> str:
        label = ENDPOINT_LABELS.get(endpoint, endpoint)
        body = _format_dict(data)
        if not body:
            return ""
        return f"=== {label} ===\n{body}"

    def _build_summary(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
        matrix_summary: str,
        rapid_data: dict[str, dict[str, Any]],
    ) -> str:
        lines = [
            f"Имя: {name}",
            f"Дата рождения: {day:02d}.{month:02d}.{year}",
            "",
            "=== КВАДРАТ ПИФАГОРА (школа Александрова) ===",
            matrix_summary,
            "",
            "=== ДАННЫЕ RAPIDAPI (the-numerology-api) ===",
        ]
        for endpoint in RAPID_NUMEROLOGY_ENDPOINTS:
            payload = rapid_data.get(endpoint)
            if not payload:
                continue
            block = self._format_endpoint_block(endpoint, payload)
            if block:
                lines.append(block)
                lines.append("")
        return "\n".join(lines).strip()

    async def fetch_full_profile(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> NumerologyProfile:
        name_parts = split_full_name(name)
        matrix = calculate_pythagoras(day, month, year)

        tasks = [
            self._fetch_endpoint(
                endpoint,
                self._endpoint_params(
                    endpoint,
                    name=name_parts,
                    day=day,
                    month=month,
                    year=year,
                ),
            )
            for endpoint in RAPID_NUMEROLOGY_ENDPOINTS
        ]
        results = await asyncio.gather(*tasks)

        rapid_data: dict[str, dict[str, Any]] = {}
        for endpoint, payload in results:
            if payload:
                rapid_data[endpoint] = payload

        if not rapid_data:
            raise NumerologyApiError(
                "Не удалось получить данные с RapidAPI. Проверьте подписку и RAPIDAPI_HOST."
            )

        summary_text = self._build_summary(
            name=name_parts.full_name,
            day=day,
            month=month,
            year=year,
            matrix_summary=matrix.format_summary(),
            rapid_data=rapid_data,
        )
        return NumerologyProfile(
            matrix_text=matrix.format_matrix(),
            summary_text=summary_text,
        )
