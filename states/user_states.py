from aiogram.fsm.state import State, StatesGroup


class FSMMakeAnAppoint(StatesGroup):
    fill_date = State()  # Ожидание выбора даты
    fill_time = State()  # Ожидание выбора времени времени
    fill_confirmation = State() # Подтверждение записи
