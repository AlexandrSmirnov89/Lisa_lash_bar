from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_appointment
from lexicon.lexicon_ru import LEXICON_RU


# стартовые кнопки
button_yes = InlineKeyboardButton(text=LEXICON_RU['yes_button'], callback_data='press_yes_start')
button_no = InlineKeyboardButton(text=LEXICON_RU['no_button'], callback_data='press_no_start')

yes_no_kb_builder = InlineKeyboardBuilder()

yes_no_kb_builder.row(button_yes, button_no)

yes_no_kb = yes_no_kb_builder.as_markup()

# основное меню
button_onl_reg = InlineKeyboardButton(text='Онлайн-запись', callback_data='onl_reg')
button_curr_reg = InlineKeyboardButton(text='Текущая запись', callback_data='c_reg')
button_examples = InlineKeyboardButton(text='Примеры работ', callback_data='ex_work')
button_history = InlineKeyboardButton(text='История посещений', callback_data='history')
button_about_me = InlineKeyboardButton(text='О мастере', callback_data='about me')

main_menu_builder = InlineKeyboardBuilder()

main_menu_builder.row(button_onl_reg, button_curr_reg, button_examples, button_history, button_about_me, width=1)

main_menu_kb: InlineKeyboardMarkup = main_menu_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

# админское меню
button_adm_add_app = InlineKeyboardButton(text='Добавить окошки', callback_data='add_app')
button_adm_change_app = InlineKeyboardButton(text='Изменить время', callback_data='change_app')

admin_menu_builder = InlineKeyboardBuilder()

admin_menu_builder.row(button_adm_add_app, button_adm_change_app, width=1)

admin_menu_kb: InlineKeyboardMarkup = admin_menu_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

# кнопки добавить еще/закончить, после добавления времени в меню админа
button_adm_add_more = InlineKeyboardButton(text='Добавить еще', callback_data='add_more')
button_adm_cancel = InlineKeyboardButton(text='К меню администратора', callback_data='admin_exit')

admin_add_more_builder = InlineKeyboardBuilder()

admin_add_more_builder.row(button_adm_add_more, button_adm_cancel, width=1)

admin_add_more_kb: InlineKeyboardMarkup = admin_add_more_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

# кнопки выбора времени
async def keyboard_free_time(date_db):
    kb_free_time = InlineKeyboardBuilder()

    appointments = await get_appointment(date_db)
    for appoint in appointments:
        if appoint.status == 'Пустая запись':
            kb_free_time.row(InlineKeyboardButton(text=str(appoint.time)[:5],
                                                  callback_data='-'.join((str(appoint.id), str(appoint.time)))))
    return kb_free_time.as_markup()


# Клавиатура подтвердить-отменить
button_confirm = InlineKeyboardButton(text='Подтверить', callback_data='confirmation')
button_cancel = InlineKeyboardButton(text='Отмена', callback_data='CANCEL')

confirmation_bilder = InlineKeyboardBuilder()

confirmation_bilder.row(button_confirm, button_cancel, width=1)

confirmation_kb: InlineKeyboardMarkup = confirmation_bilder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)