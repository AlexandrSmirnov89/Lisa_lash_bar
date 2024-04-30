from aiogram import F, Router
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.filters import Command, CommandStart
from keyboards.keyboards import yes_no_kb, main_menu_kb
from lexicon.lexicon_ru import LEXICON_RU
#from services.services import get_bot_choice, get_winner

import aiogram_calendar

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=yes_no_kb)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=yes_no_kb)


@router.callback_query(F.data == 'press_yes_start')
async def process_yes_answer(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['yes'], reply_markup=main_menu_kb)


@router.callback_query(F.data == 'press_no_start')
async def process_no_answer(message: Message):
    await message.answer(text=LEXICON_RU['no'])


@router.callback_query(F.data == 'onl_reg')
async def process_online_reg(callback: CallbackQuery):
    kb_calendar = await aiogram_calendar.SimpleCalendar().start_calendar()
    for button in kb_calendar.inline_keyboard:
        print(button)
    await callback.message.edit_text(text='Выберете дату',
                                     reply_markup=kb_calendar)
