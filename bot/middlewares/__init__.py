from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.config import Settings
from bot.services.ai_interpreter import AiInterpreter
from bot.services.numerology_api import NumerologyApiClient


class ServicesMiddleware(BaseMiddleware):
    def __init__(
        self,
        settings: Settings,
        numerology_api: NumerologyApiClient,
        ai: AiInterpreter,
    ) -> None:
        self._settings = settings
        self._numerology_api = numerology_api
        self._ai = ai

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self._settings
        data["numerology_api"] = self._numerology_api
        data["ai"] = self._ai
        return await handler(event, data)


__all__ = ["ServicesMiddleware"]
