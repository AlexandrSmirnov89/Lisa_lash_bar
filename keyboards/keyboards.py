from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

# кнопки календаря