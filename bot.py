import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import Config, load_config
from handlers import admin_handlers, user_handlers, other_handlers
from database.models import async_main
from middlewares.outer import AdminsMiddleware

# Инициализируем логгер
logger = logging.getLogger(__name__)


async def main():
    await async_main()

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    config: Config = load_config()
    
    # redis = Redis(host='localhost', port=6379)

    # storage = RedisStorage(redis=redis)
    storage = MemoryStorage()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    dp = Dispatcher(storage=storage)

    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # admin_handlers.router.callback_query.outer_middleware(AdminsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())