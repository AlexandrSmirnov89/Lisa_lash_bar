from aiogram import F, Router
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove)
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendarCallback
from keyboards.keyboards import yes_no_kb, main_menu_kb, keyboard_free_time, confirmation_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import CalendarRegistration
from states.user_states import FSMMakeAnAppoint
from database.requests import get_appointment, change_of_status, get_all_appointment, get_curr_user_appoint
from datetime import date

router: Router = Router()


@router.message(CommandStart(), default_state)
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=yes_no_kb)


@router.message(Command(commands='help'), default_state)
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=yes_no_kb)


@router.message(Command(commands='cancel'))
async def process_cancel_state(message: Message,
                               state: FSMContext):
    await message.answer(text='Вы вышли из состояния записи и попали в главное меню',
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(text=LEXICON_RU['yes'], reply_markup=main_menu_kb)

    await state.clear()
    

@router.callback_query(F.data == 'press_yes_start', default_state)
async def process_yes_answer(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['yes'], reply_markup=main_menu_kb)


@router.callback_query(F.data == 'press_no_start', default_state)
async def process_no_answer(message: Message):
    await message.answer(text=LEXICON_RU['no'])


@router.callback_query(SimpleCalendarCallback.filter(F.act == 'CANCEL'), StateFilter(FSMMakeAnAppoint.fill_date))
@router.callback_query(F.data == 'CANCEL', ~StateFilter(default_state))
async def process_cancel_state(callback: CallbackQuery,
                               state: FSMContext):
    await callback.message.edit_text(text='Вы вышли из состояния записи и попали в главное меню',
                                     reply_markup=main_menu_kb)

    await state.clear()
    
    
@router.callback_query(F.data == 'c_reg', default_state)
async def process_online_reg(callback: CallbackQuery):
    resault = await get_curr_user_appoint(callback.from_user.id)

    await callback.message.edit_text(text=f'''Текущие записи:
                                     {[(line.date, line.time) for line in resault]}''',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='cancel', callback_data='press_yes_start')]]))
    

@router.callback_query(F.data == 'ex_work', default_state)
async def process_ex_work(callback: CallbackQuery):
    ...

@router.callback_query(StateFilter(FSMMakeAnAppoint.fill_date), SimpleCalendarCallback.filter(F.act == 'PREV-MONTH'))
@router.callback_query(F.data == 'onl_reg', default_state)
async def process_online_reg(callback: CallbackQuery, state: FSMContext):
    kb = await CalendarRegistration.get_current_month()
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text='Выберите дату',
                                     reply_markup=kb)

    await state.set_state(FSMMakeAnAppoint.fill_date)


@router.callback_query(StateFilter(FSMMakeAnAppoint.fill_date),
                       SimpleCalendarCallback.filter(F.act == 'NEXT-MONTH'))
async def process_next_month(callback: CallbackQuery,
                             state: FSMContext):
    kb = await CalendarRegistration.get_next_month()
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f'Выберите дату',
                                     reply_markup=kb)

    await state.set_state(FSMMakeAnAppoint.fill_date)


@router.callback_query(StateFilter(FSMMakeAnAppoint.fill_date), SimpleCalendarCallback.filter(F.act == 'DAY'))
async def process_selected_date(callback: CallbackQuery,
                                callback_data: SimpleCalendarCallback,
                                state: FSMContext):
    selected_date = callback_data.year, callback_data.month, callback_data.day
    await state.update_data(sel_date=date(*selected_date))

    await callback.message.edit_text(text='Выберите время',
                                     reply_markup=await keyboard_free_time(date(*selected_date)))

    await state.set_state(FSMMakeAnAppoint.fill_time)


@router.callback_query(StateFilter(FSMMakeAnAppoint.fill_time))
async def process_selected_time(callback: CallbackQuery,
                                state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(app_id=callback.data.split('-')[0], sel_time=callback.data.split('-')[-1])

    await callback.message.answer(text=f'Ваша запись {user_data["sel_date"]} {callback.data.split("-")[-1]}Для подтверждения поделитесь номером телефонаДля отмены отправьте команду /cancel',
                                     reply_markup=confirmation_kb)

    await state.set_state(FSMMakeAnAppoint.fill_confirmation)


@router.message(StateFilter(FSMMakeAnAppoint.fill_confirmation))
async def process_confirmation(message: Message,
                               state: FSMContext):
    user_data = await state.get_data()
    print(message.model_dump_json(indent=4))
    await change_of_status(appoint_id=user_data['app_id'], status='Подтверждено', user_data=message.contact)
    await message.answer(text=f'''Ваша запись {user_data["sel_date"]} {user_data["sel_time"]} успешно подтверждена
                         Номер телефона сохранен''', reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text=f'Ваша запись {user_data["sel_date"]} {user_data["sel_time"]} успешно подтверждена',
        reply_markup=main_menu_kb)

    await state.clear()
