import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from database import get_db_connection

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот для поиска проектов.")

async def main():
    await dp.start_polling(bot)


async def test_db():
    conn = await get_db_connection()
    version = await conn.fetchval("SELECT version();")
    print(f"Подключено к PostgreSQL: {version}")
    await conn.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_db())  # Тест БД
    asyncio.run(main())     # Запуск бота
