from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
import asyncio


async def fucs():
    kb_calendar = await SimpleCalendar().start_calendar()
    for buttons in kb_calendar.inline_keyboard:
        for button in buttons:
            print(button.text, '->', button.callback_data)


if __name__ == '__main__':
    asyncio.run(fucs())
