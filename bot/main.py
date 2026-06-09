import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.handlers import router
from bot.middlewares import ServicesMiddleware
from bot.services.ai_interpreter import AiInterpreter
from bot.services.numerology_api import NumerologyApiClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = load_settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    numerology_api = NumerologyApiClient(settings)
    ai = AiInterpreter(settings)

    services = ServicesMiddleware(settings, numerology_api, ai)
    dp.message.middleware(services)
    dp.callback_query.middleware(services)
    dp.include_router(router)

    logger.info("AI Numerolog bot started (ai=%s)", ai.enabled)
    await dp.start_polling(bot)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
