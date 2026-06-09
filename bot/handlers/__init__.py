from aiogram import Router

from bot.handlers.common import router as common_router
from bot.handlers.numerology import router as numerology_router

router = Router()
router.include_router(common_router)
router.include_router(numerology_router)
