from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

BASE_PATH = "/v1/numerology"

RAPIDAPI_ENDPOINTS: tuple[tuple[str, str], ...] = (
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
    """Нумерология: calc-сервис (полный профиль) + RapidAPI numerology-api4."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "x-rapidapi-key": settings.rapidapi_key,
            "x-rapidapi-host": settings.rapidapi_host,
            "Content-Type": "application/json",
        }
        self._rapidapi_base = f"https://{settings.rapidapi_host}"
        self._numerology_base = f"{self._rapidapi_base}{BASE_PATH}"
        self._calc_url = settings.calc_service_url

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

    async def _rapidapi_post(self, url: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self._headers, json=payload)
        except httpx.HTTPError as exc:
            logger.warning("RapidAPI POST %s network error: %s", url, exc)
            return None

        if response.status_code >= 400:
            logger.warning("RapidAPI POST %s -> %s: %s", url, response.status_code, response.text[:300])
            return None

        try:
            return response.json()
        except ValueError:
            return None

    async def _post_numerology(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        return await self._rapidapi_post(f"{self._numerology_base}/{endpoint}", payload)

    async def _fetch_one(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> tuple[str, dict[str, Any] | None]:
        data = await self._post_numerology(endpoint, payload)
        return endpoint, data

    async def _fetch_full_profile_from_calc(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> str:
        url = f"{self._calc_url}/v1/full-profile"
        body = {
            "name": name,
            "day": day,
            "month": month,
            "year": year,
            "current_year": date.today().year,
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=body)
        except httpx.HTTPError as exc:
            raise NumerologyApiError("Сервис нумерологического расчёта недоступен.") from exc

        if response.status_code >= 400:
            logger.error("Calc service %s -> %s: %s", url, response.status_code, response.text[:300])
            raise NumerologyApiError("Не удалось получить расчёт с сервиса нумерологии.")

        data = response.json()
        summary = data.get("summary")
        if not summary:
            raise NumerologyApiError("Сервис расчёта вернул пустой профиль.")
        return summary

    async def fetch_supplementary(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        payload = self._person_payload(name=name, day=day, month=month, year=year)
        tasks = [self._fetch_one(ep, payload) for ep, _ in RAPIDAPI_ENDPOINTS]
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

        lines = ["=== ДОПОЛНИТЕЛЬНО (RapidAPI numerology-api4) ==="]
        labels = dict(RAPIDAPI_ENDPOINTS)
        for endpoint, detail in data.items():
            label = labels.get(endpoint, endpoint)
            number = detail.get("number", "—")
            message = detail.get("message", "")
            lines.append(f"- {label}: {number}")
            if message:
                lines.append(f"  {message}")
        return "\n".join(lines)

    async def fetch_full_profile(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> str:
        profile_task = self._fetch_full_profile_from_calc(
            name=name, day=day, month=month, year=year
        )
        extra_task = self.fetch_supplementary(name=name, day=day, month=month, year=year)
        profile_text, extra = await asyncio.gather(profile_task, extra_task)

        parts = [profile_text]
        extra_text = self.format_supplementary(extra)
        if extra_text:
            parts.append(extra_text)
        return "\n\n".join(parts)
