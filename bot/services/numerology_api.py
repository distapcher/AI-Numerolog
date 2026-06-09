from __future__ import annotations

import logging
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)


class NumerologyApiError(Exception):
    pass


class NumerologyApiClient:
    """Дополнительные нумерологические данные через RapidAPI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "x-rapidapi-key": settings.rapidapi_key,
            "x-rapidapi-host": settings.rapidapi_host,
        }
        self._base = f"https://{settings.rapidapi_host}"

    async def _get(self, path: str, params: dict[str, str]) -> dict[str, Any] | None:
        url = f"{self._base}{path}"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=self._headers, params=params)
        except httpx.HTTPError as exc:
            logger.warning("Numerology API %s network error: %s", path, exc)
            return None

        if response.status_code >= 400:
            logger.warning(
                "Numerology API %s -> %s: %s",
                path,
                response.status_code,
                response.text[:300],
            )
            return None

        try:
            return response.json()
        except ValueError:
            logger.warning("Numerology API %s: invalid JSON", path)
            return None

    @staticmethod
    def _split_name(full_name: str) -> tuple[str, str, str]:
        parts = [p for p in full_name.split() if p]
        if not parts:
            return "User", "", ""
        if len(parts) == 1:
            return parts[0], "", ""
        if len(parts) == 2:
            return parts[0], "", parts[1]
        return parts[0], " ".join(parts[1:-1]), parts[-1]

    async def fetch_supplementary(
        self,
        *,
        name: str,
        day: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        """Life path, expression, soul urge — если API доступен."""
        result: dict[str, Any] = {}
        date_params = {
            "year": str(year),
            "month": str(month),
            "day": str(day),
            "birth_year": str(year),
            "birth_month": str(month),
            "birth_day": str(day),
        }

        life_path = await self._get("/life_path", date_params)
        if life_path:
            result["life_path"] = life_path

        first, middle, last = self._split_name(name)
        name_params = {
            "first_name": first,
            "middle_name": middle,
            "last_name": last,
        }
        for endpoint, key in (
            ("/expression_number", "expression"),
            ("/soul_urge", "soul_urge"),
            ("/personality_number", "personality"),
        ):
            data = await self._get(endpoint, name_params)
            if data:
                result[key] = data

        return result

    def format_supplementary(self, data: dict[str, Any]) -> str:
        if not data:
            return ""
        lines = ["Дополнительные данные (RapidAPI Numerology):"]
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
