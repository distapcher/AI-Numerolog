from __future__ import annotations

import logging
import re

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)


class AiInterpreter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._enabled = bool(settings.openai_api_key)
        self._system_prompt: str | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _load_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt
        path = self._settings.prompt_path
        if path.exists():
            self._system_prompt = path.read_text(encoding="utf-8")
            return self._system_prompt
        logger.warning("Prompt not found: %s", path)
        self._system_prompt = ""
        return self._system_prompt

    @staticmethod
    def _clean_output(text: str) -> str:
        text = text.replace("**", "")
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        return text.strip()

    async def interpret(
        self,
        *,
        name: str,
        birth_date: str,
        numerology_data: str,
    ) -> str:
        if not self._enabled:
            raise RuntimeError("ИИ не настроен (нет OPENAI_API_KEY)")

        system_prompt = self._load_system_prompt()
        if not system_prompt:
            raise RuntimeError(f"Файл системного промпта не найден: {self._settings.prompt_path}")

        user_content = (
            f"ДАННЫЕ ДЛЯ АНАЛИЗА:\n"
            f"- ФИО: {name}\n"
            f"- Дата рождения (формат ДД.ММ.ГГГГ): {birth_date}\n\n"
            "РАССЧИТАННЫЕ НУМЕРОЛОГИЧЕСКИЕ ДАННЫЕ "
            "(используй как основу расчётов, не пересчитывай самостоятельно):\n\n"
            f"{numerology_data}\n\n"
            "Проведи анализ строго по структуре из системного промпта (все 20 разделов). "
            "Обращайся к человеку только на «вы». "
            "Не используй символы * и # и markdown. "
            "Не используй эмодзи. "
            "Каждый вывод опирай на конкретные числа из данных выше."
        )

        url = f"{self._settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": self._settings.ai_max_tokens,
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(url, json=body, headers=headers)

        if response.status_code >= 400:
            logger.error("LLM error %s: %s", response.status_code, response.text[:500])
            raise RuntimeError("Не удалось получить описание от ИИ.")

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("Пустой ответ от ИИ.")
        return self._clean_output(choices[0]["message"]["content"].strip())
