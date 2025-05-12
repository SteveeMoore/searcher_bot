import os
import sys
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from loguru import logger
from database import search_projects, check_db_connection

# Загрузка переменных окружения
load_dotenv()

# Настройка логгера
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    colorize=True,
    level="INFO"
)
logger.add(
    "debug.log",
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG"
)


class SecureBot(Bot):
    """Кастомный бот с маскировкой токена в логах"""

    def __init__(self, token: str):
        super().__init__(token)
        logger.debug("Инициализация бота с токеном: ******")


# Инициализация бота и диспетчера
bot = SecureBot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    logger.info(f"Новый пользователь: {user.full_name} (ID: {user.id})")
    await message.answer("Привет! Введите название проекта для поиска PDF.")


@dp.message(F.text)
async def handle_search(message: types.Message):
    """Обработчик поисковых запросов"""
    try:
        query = message.text.strip()
        user_id = message.from_user.id

        logger.bind(user_id=user_id).debug(f"Запрос: '{query}'")
        results = await search_projects(query)

        if not results:
            logger.warning(f"По запросу '{query}' ничего не найдено")
            return await message.answer("Ничего не найдено 😔")

        logger.success(f"Найдено проектов: {len(results)}")
        response = ["🔍 Результаты поиска:"]
        for project in results:
            response.append(f"• {project['name']}: {project['url']}")

        await message.answer("\n".join(response))

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("⚠️ Произошла ошибка при поиске")


async def main():
    """Основная функция запуска бота"""
    if not await check_db_connection():
        logger.critical("Не удалось подключиться к базе данных")
        return

    logger.info("🟢 Бот запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
    finally:
        logger.info("🔴 Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())