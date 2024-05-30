from aiogram.fsm.state import State, StatesGroup


class FSMAddingTime(StatesGroup):
    fill_date = State()  # Ожидание выбора даты
    fill_time = State()  # Ожидание ввода времени
