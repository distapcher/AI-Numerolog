from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.services.ai_interpreter import AiInterpreter
from bot.services.messaging import send_long_text
from bot.services.numerology_api import NumerologyApiClient
from bot.services.numerology_calc import calculate_pythagoras, parse_birth_date
from bot.states import NumerologyStates

logger = logging.getLogger(__name__)
router = Router()


async def _start_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(NumerologyStates.name)
    await message.answer(
        "Введите <b>имя</b> для анализа (или «—», если без имени):",
    )


@router.message(Command("analyze"))
@router.message(F.text == "🔢 Нумерологический анализ")
async def start_analysis(message: Message, state: FSMContext, ai: AiInterpreter) -> None:
    if not ai.enabled:
        await message.answer(
            "Сервис анализа временно недоступен: не настроен <code>OPENAI_API_KEY</code>."
        )
        return
    await _start_flow(message, state)


@router.message(NumerologyStates.name)
async def on_name(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    name = "Гость" if raw in {"", "—", "-"} else raw[:64]
    await state.update_data(name=name)
    await state.set_state(NumerologyStates.birth_date)
    await message.answer("Дата рождения (<code>ДД.ММ.ГГГГ</code>):")


@router.message(NumerologyStates.birth_date)
async def on_birth_date(
    message: Message,
    state: FSMContext,
    ai: AiInterpreter,
    numerology_api: NumerologyApiClient,
) -> None:
    try:
        year, month, day = parse_birth_date(message.text or "")
    except ValueError as exc:
        await message.answer(str(exc))
        return

    data = await state.get_data()
    name = data.get("name", "Гость")
    await state.clear()

    status = await message.answer("⏳ Рассчитываю квадрат Пифагора…")
    matrix = calculate_pythagoras(day, month, year)

    await status.edit_text("⏳ Запрашиваю дополнительные данные…")
    extra = await numerology_api.fetch_supplementary(
        name=name,
        day=day,
        month=month,
        year=year,
    )
    extra_text = numerology_api.format_supplementary(extra)

    numerology_data = matrix.format_summary()
    if extra_text:
        numerology_data = f"{numerology_data}\n\n{extra_text}"

    await status.edit_text(
        "✅ Расчёт готов.\n\n"
        f"<pre>{matrix.format_summary()}</pre>\n\n"
        "⏳ Готовлю расшифровку через ИИ (это может занять несколько минут)…"
    )

    try:
        analysis = await ai.interpret(name=name, numerology_data=numerology_data)
    except Exception:
        logger.exception("AI interpretation failed")
        await message.answer(
            "Не удалось получить расшифровку от ИИ. Попробуйте позже."
        )
        return

    await send_long_text(message, analysis, title="Нумерологический анализ")
