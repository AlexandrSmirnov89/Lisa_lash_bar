from aiogram import F, Router
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, InputMediaPhoto)
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram_calendar import SimpleCalendarCallback
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import admin_menu_kb, admin_add_more_kb, admin_change_example_kb, keyboard_category, keyboard_free_time
from lexicon.lexicon_ru import LEXICON_RU
from services.services import CalendarRegistration
from database.requests import add_free_appointment, get_appointment, get_all_appointment, add_photo, get_category_photos, get_photos, del_photo, del_category, del_appoint
from config_data.config import Config, load_config
from states.admin_states import FSMAddingTime, FSMDelPhotos, FSMDelCategory, FSMDelAppoint
from datetime import datetime, date, time

router = Router()
config: Config = load_config()


@router.message(Command(commands='admin'), F.from_user.id == int(config.admins.admins))
async def process_admin_command(message: Message, state: FSMContext):
    await message.answer(text=f'В данном меню вы можете выбрать следующие действия',
                         reply_markup=admin_menu_kb)
    
    await state.clear()


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


@router.callback_query(F.data == 'change_example',
                       F.from_user.id == int(config.admins.admins))
async def process_change_example(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите категорию',
                                     reply_markup=admin_change_example_kb)
    

@router.callback_query(F.data == 'add_example',
                       F.from_user.id == int(config.admins.admins))
async def processs_adding_photos(callback: CallbackQuery):
    await callback.message.edit_text(text='Отправьте изображение вместе с названием категории (отправлять необходимо одним сообщением)')
    

@router.message(F.photo,
                F.from_user.id == int(config.admins.admins), 
                StateFilter(default_state))
async def process_take_photo(message: Message):
    await add_photo(url_photo=message.photo[0].file_id, category=message.caption)
    
    await message.answer(text='Вы можете продолжить добавлять фотографии. Удалить фотографии можно по кнопке "удалить пример". Для выхода в меню отправьте команду /admin')
    
    
@router.callback_query(F.data == 'del_example', StateFilter(default_state))
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Выберите категорию', reply_markup=await keyboard_category())
    
    await state.set_state(FSMDelPhotos.fill_category)
    

@router.callback_query(F.data.startswith('category'), StateFilter(FSMDelPhotos.fill_category))
async def process_select_photo(callback: CallbackQuery, state: FSMContext):
    photos = await get_photos(category=callback.data.split(':')[1])
    media = [InputMediaPhoto(media=photo) for photo in photos]

    await callback.bot.send_media_group(chat_id=callback.from_user.id, media=media)
    
    await state.set_state(FSMDelPhotos.waiting_photo)
    

@router.message(StateFilter(FSMDelPhotos.waiting_photo))
async def process_del_photo(message: Message, state: FSMContext):
    await del_photo(message.photo[0].file_id)
    
    await state.clear()
    
    
@router.callback_query(F.data == 'del_category', 
                       F.from_user.id == int(config.admins.admins),
                       StateFilter(default_state))
async def process_del_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите категорию, которую хотите удалить. Все фотографии удалятся вместе с ней', reply_markup=await keyboard_category())
    
    await state.set_state(FSMDelCategory.fill_category)
    

@router.callback_query(F.data.startswith('category'), StateFilter(FSMDelCategory.fill_category))
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    await del_category(category=callback.data.split(':')[1])
    
    await callback.message.answer(text='Категория удалена, можете продолжить или вернуться в главное меню админа нажав /cancel', 
                                  reply_markup=admin_change_example_kb)
    
    await state.clear()

    
@router.callback_query(F.data == 'change_app', 
                       F.from_user.id == int(config.admins.admins))
@router.callback_query(StateFilter(FSMDelAppoint.fill_date), SimpleCalendarCallback.filter(F.act == 'PREV-MONTH'))
async def process_del_reg(callback: CallbackQuery, state: FSMContext):
    kb = await CalendarRegistration.get_current_month()
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text='Выберите дату',
                                     reply_markup=kb)

    await state.set_state(FSMDelAppoint.fill_date)


@router.callback_query(StateFilter(FSMDelAppoint.fill_date),
                       SimpleCalendarCallback.filter(F.act == 'NEXT-MONTH'))
async def process_next_month(callback: CallbackQuery,
                             state: FSMContext):
    kb = await CalendarRegistration.get_next_month()
    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f'Выберите дату, в которую хотите изменить время. Для выхода нажмите кнопку "cancel"',
                                     reply_markup=kb)

    await state.set_state(FSMDelAppoint.fill_date)
    
    
@router.callback_query(StateFilter(FSMDelAppoint.fill_date), SimpleCalendarCallback.filter(F.act == 'DAY'))
async def process_selected_date(callback: CallbackQuery,
                                callback_data: SimpleCalendarCallback,
                                state: FSMContext):
    selected_date = callback_data.year, callback_data.month, callback_data.day
    await state.update_data(sel_date=date(*selected_date))

    await callback.message.edit_text(text='Выберите время которое хотите убрать',
                                     reply_markup=await keyboard_free_time(date(*selected_date)))

    await state.set_state(FSMDelAppoint.fill_time)
    
    
@router.callback_query(StateFilter(FSMDelAppoint.fill_time))
async def process_selected_time(callback: CallbackQuery,
                                state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(app_id=callback.data.split('-')[0], sel_time=callback.data.split('-')[-1])
    
    await del_appoint(appoint_id=callback.data.split('-')[0])

    await callback.message.answer(text=f'Вы стерли запись {user_data["sel_date"]} {callback.data.split("-")[-1]}, для выхода в меню отправьте коанду /admin')

    await state.clear()

