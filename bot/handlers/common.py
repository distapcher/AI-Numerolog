from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.keyboards import main_menu_kb
from bot.services.ai_interpreter import AiInterpreter

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я <b>ИИ-нумеролог</b>.\n\n"
        "По дате рождения и имени рассчитаю квадрат Пифагора и проведу "
        "глубокий анализ личности: предназначение, таланты, финансы, "
        "дело жизни и зоны роста.\n\n"
        "Нажми «🔢 Нумерологический анализ» для запуска.",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message, ai: AiInterpreter) -> None:
    ai_note = (
        "ИИ подключён — анализ доступен."
        if ai.enabled
        else "⚠️ ИИ не настроен — анализ недоступен."
    )
    await message.answer(
        "<b>Как пользоваться</b>\n\n"
        "1. /analyze — начать анализ\n"
        "2. Имя (или «—»)\n"
        "3. Дата: <code>ДД.ММ.ГГГГ</code>\n\n"
        "Бот рассчитает квадрат Пифагора и подготовит расшифровку через ИИ.\n\n"
        f"{ai_note}",
        reply_markup=main_menu_kb(),
    )
