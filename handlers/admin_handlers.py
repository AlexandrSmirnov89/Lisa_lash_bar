from aiogram import F, Router
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram_calendar import SimpleCalendarCallback
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import admin_menu_kb, admin_add_more_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import CalendarRegistration
from database.requests import add_free_appointment, get_appointment, get_all_appointment
from config_data.config import Config, load_config
from states.admin_states import FSMAddingTime
from datetime import datetime, date, time

router = Router()
config: Config = load_config()


@router.message(Command(commands='admin'), F.from_user.id == int(config.admins.admins))
async def process_admin_command(message: Message):
    await message.answer(text=f'В данном меню вы можете выбрать следующие действия',
                         reply_markup=admin_menu_kb)


@router.callback_query(SimpleCalendarCallback.filter(F.act == 'CANCEL'), StateFilter(FSMAddingTime.fill_date))
@router.callback_query(StateFilter(FSMAddingTime.fill_time),
                       F.data == 'admin_exit',
                       F.from_user.id == int(config.admins.admins))
async def process_ext_in_main_menu(callback: CallbackQuery,
                                   state: FSMContext):
    await callback.message.edit_text(text=f'В данном меню вы можете выбрать следующие действия',
                                     reply_markup=admin_menu_kb)
    await state.clear()


@router.callback_query(StateFilter(FSMAddingTime.fill_date), SimpleCalendarCallback.filter(F.act == 'PREV-MONTH'))
@router.callback_query(F.data == 'add_app', StateFilter(default_state))
async def process_get_calendar(callback: CallbackQuery, state: FSMContext):
    kb = await CalendarRegistration.get_current_month(admin=True)
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f'Для добавления времени выберете дату',
                                     reply_markup=kb)

    await state.set_state(FSMAddingTime.fill_date)


@router.callback_query(StateFilter(FSMAddingTime.fill_date),
                       SimpleCalendarCallback.filter(F.act == 'NEXT-MONTH'),
                       F.from_user.id == int(config.admins.admins))
async def process_next_month(callback: CallbackQuery,
                             state: FSMContext):
    kb = await CalendarRegistration.get_next_month(admin=True)
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f'Для добавления времени выберете дату',
                                     reply_markup=kb)

    await state.set_state(FSMAddingTime.fill_date)


@router.callback_query(StateFilter(FSMAddingTime.fill_date),
                       SimpleCalendarCallback.filter(F.act == 'DAY'),
                       F.from_user.id == int(config.admins.admins))
async def process_add_free_appointment(callback: CallbackQuery,
                                       callback_data: SimpleCalendarCallback,
                                       state: FSMContext):
    selected_date = callback_data.year, callback_data.month, callback_data.day

    await state.update_data(sel_date=date(*selected_date))
    appointments = await get_appointment(date(*selected_date))

    await callback.message.edit_text(f'На дату {str(selected_date)} имеются следующие места:'
                                     f'{[str(t.time) for t in appointments]}'
                                     f'Введите новое время в формате HH:MM')
    await state.set_state(FSMAddingTime.fill_time)
    # await add_free_appointment(date=date(year=callback_data.year, month=callback_data.month, day=callback_data.day),
    #                            time=time(hour=18, minute=00))
    # await callback.message.answer(text='Запись добавлена')


@router.message(StateFilter(FSMAddingTime.fill_time),
                F.from_user.id == int(config.admins.admins), F.text)
async def process_write_time(message: Message, state: FSMContext):
    user_dict = await state.get_data()
    await add_free_appointment(date=user_dict["sel_date"],
                               time=time(*map(int, message.text.split(':'))))
    await message.answer(f'На {user_dict["sel_date"]} было добавлено новое время: '
                         f'{message.text}',
                         reply_markup=admin_add_more_kb)


@router.callback_query(StateFilter(FSMAddingTime.fill_time),
                       F.data == 'add_more',
                       F.from_user.id == int(config.admins.admins))
async def process_add_more_app(callback: CallbackQuery,
                               state: FSMContext):
    kb = await CalendarRegistration.get_current_month(admin=True)
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f'Для добавления времени выберете дату',
                                     reply_markup=kb)

    await state.set_state(FSMAddingTime.fill_date)


@router.callback_query(StateFilter(FSMAddingTime.fill_time),
                       F.data == 'admin_exit',
                       F.from_user.id == int(config.admins.admins))
async def process_ext_in_main_menu(callback: CallbackQuery,
                                   state: FSMContext):
    await callback.message.edit_text(text=f'В данном меню вы можете выбрать следующие действия',
                                     reply_markup=admin_menu_kb)
    await state.clear()
