#TODO 
# на респонсы добавить кнпоку выхода в старт СДЕЛАНО №№№№№№№№№№№№№№ праздник
# добавить возможность просмотра онлайн-стаффа СДЕЛАНО №№№№№№№№№№№№№№ праздник
# добавить возможность просмотра гильдий
# добавить возможность следить за игрком (уведомления когда зайдет в игру) СЛОЖНО

import asyncio
from aiogram import Bot, Dispatcher
from handlers.routes import router
from config import TOKEN

dp = Dispatcher()
dp.include_router(router)


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt):
        print("Bot stopped")