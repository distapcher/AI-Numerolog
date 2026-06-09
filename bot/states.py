from aiogram.fsm.state import State, StatesGroup


class NumerologyStates(StatesGroup):
    name = State()
    birth_date = State()
