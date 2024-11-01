from aiogram.fsm.state import State, StatesGroup


class FSMAddingTime(StatesGroup):
    fill_date = State()  # Ожидание выбора даты
    fill_time = State()  # Ожидание ввода времени


class FSMDelPhotos(StatesGroup):
    fill_category = State()
    waiting_photo = State()
    
    
class FSMDelCategory(StatesGroup):
    fill_category = State()


class FSMDelAppoint(StatesGroup):
    fill_date =  State()
    fill_time = State()
    fill_comfirmation = State()