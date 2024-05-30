from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from config_data.config import Config, load_config


config: Config = load_config()


class AdminsMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user: User = data.get('event_from_user')
        if user and user.id == int(config.admins.admins):
            return await handler(event, data)

