from aiogram_calendar import SimpleCalendar
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.requests import get_all_appointment
from datetime import datetime, date
import asyncio


class CalendarRegistration:
    @staticmethod
    async def _process_check_date(kb, admin=False):
        date_db = await get_all_appointment()

        if admin:
            date_db = [line.date for line in date_db if line.date >= datetime.now().date()]
        else:
            date_db = [line.date for line in date_db
                       if line.date >= datetime.now().date() and line.status == 'Пустая запись']

        for buttons in kb[3:-1]:
            for button in buttons:
                tag, act, year, month, day = button.callback_data.split(':')
                if act == 'DAY' and date(int(year), int(month), int(day)) not in date_db:
                    act = 'IGNORE'
                    year, month, day = '', '', ''
                    button.callback_data = ':'.join([tag, act, year, month, day])
                    button.text = ' '
        return kb[1:]

    @classmethod
    async def get_current_month(cls, admin=False):
        kb_calendar = await SimpleCalendar().start_calendar()
        kb_calendar = kb_calendar.inline_keyboard
        kb_calendar[1][0].text = ' '
        kb_calendar[1][0].callback_data = 'simple_calendar:IGNORE:::'
        if admin:
            return kb_calendar
        else:
            res = await cls._process_check_date(kb_calendar)
            return res

    @classmethod
    async def get_next_month(cls, admin=False):
        kb_calendar = await SimpleCalendar().start_calendar(month=datetime.now().month + 1)
        kb_calendar = kb_calendar.inline_keyboard
        kb_calendar[1][-1].text = ' '
        kb_calendar[1][-1].callback_data = 'simple_calendar:IGNORE:::'
        if admin:
            return kb_calendar
        else:
            res = await cls._process_check_date(kb_calendar)
            return res
