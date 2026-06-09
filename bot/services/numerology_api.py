from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

BASE_PATH = "/v1/numerology"

ENDPOINTS: tuple[tuple[str, str], ...] = (
    ("destiny", "Число судьбы (Destiny)"),
    ("personality", "Число личности (Personality)"),
    ("character", "Число характера (Character)"),
    ("soul-urge", "Число души (Soul Urge)"),
    ("attitude", "Число отношения (Attitude)"),
    ("hidden-agenda", "Скрытая повестка (Hidden Agenda)"),
    ("divine-purpose", "Божественное предназначение (Divine Purpose)"),
    ("personal-year", "Личный год (Personal Year)"),
)


class NumerologyApiError(Exception):
    pass


class NumerologyApiClient:
    """Нумерологические данные через numerology-api4 (javathinked)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "x-rapidapi-key": settings.rapidapi_key,
            "x-rapidapi-host": settings.rapidapi_host,
            "Content-Type": "application/json",
        }
        self._base = f"https://{settings.rapidapi_host}{BASE_PATH}"

    @staticmethod
    def _split_name(full_name: str) -> tuple[str, str]:
        parts = [p for p in full_name.split() if p]
        if not parts:
            return "User", "Guest"
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[-1]

    def _person_payload(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        first_name, last_name = self._split_name(name)
        return {
            "firstName": first_name,
            "lastName": last_name or first_name,
            "day": day,
            "month": month,
            "year": year,
            "phoneNumber": "+70000000000",
            "email": "user@numerolog.bot",
            "language": "en",
        }

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        url = f"{self._base}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self._headers, json=payload)
        except httpx.HTTPError as exc:
            logger.warning("Numerology API %s network error: %s", endpoint, exc)
            return None

        if response.status_code >= 400:
            logger.warning(
                "Numerology API %s -> %s: %s",
                endpoint,
                response.status_code,
                response.text[:300],
            )
            return None

        try:
            return response.json()
        except ValueError:
            logger.warning("Numerology API %s: invalid JSON", endpoint)
            return None

    async def _fetch_one(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> tuple[str, dict[str, Any] | None]:
        data = await self._post(endpoint, payload)
        return endpoint, data

    async def fetch_supplementary(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        payload = self._person_payload(name=name, day=day, month=month, year=year)
        tasks = [self._fetch_one(ep, payload) for ep, _ in ENDPOINTS]
        results = await asyncio.gather(*tasks)

        output: dict[str, Any] = {}
        for endpoint, data in results:
            if not data or data.get("statusValue") != 200:
                continue
            detail = data.get("detail") or {}
            output[endpoint] = detail
        return output

    def format_supplementary(self, data: dict[str, Any]) -> str:
        if not data:
            return ""

        lines = ["Данные Numerology API (numerology-api4):"]
        labels = dict(ENDPOINTS)
        for endpoint, detail in data.items():
            label = labels.get(endpoint, endpoint)
            number = detail.get("number", "—")
            message = detail.get("message", "")
            lines.append(f"- {label}: {number}")
            if message:
                lines.append(f"  {message}")
        return "\n".join(lines)
