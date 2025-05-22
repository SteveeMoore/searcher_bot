import os
import sys
import asyncio
from dotenv import load_dotenv
from loguru import logger
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    add_project_to_db,
    delete_project_from_db,
    get_all_projects,
    search_projects,
    check_db_connection,
)

# Загрузка переменных окружения
load_dotenv()

# Настройка логгера
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    colorize=True,
    level="INFO",
)
logger.add(
    "debug.log",
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG",
)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i}


class BotStates(StatesGroup):
    project_name = State()
    project_url = State()
    project_synonyms = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    user = message.from_user
    logger.info(f"Новый пользователь: {user.full_name} (ID: {user.id})")
    await message.answer("Привет! Введите название проекта для поиска PDF.")


@dp.message(Command("admin"))
async def admin_menu(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Доступ запрещен!")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="Добавить проект"), types.KeyboardButton(text="Удалить проект")]
    ])
    await message.answer("Админ-панель:", reply_markup=keyboard)


@dp.message(F.text == "Добавить проект")
async def add_project_start(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Доступ запрещен!")

    await state.set_state(BotStates.project_name)
    await message.answer("Введите название проекта:", reply_markup=types.ReplyKeyboardRemove())


@dp.message(BotStates.project_name)
async def process_project_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(BotStates.project_url)
    await message.answer("Введите URL проекта:")


@dp.message(BotStates.project_url)
async def process_project_url(message: types.Message, state: FSMContext) -> None:
    if not message.text.startswith("http"):
        return await message.answer("❌ Некорректный URL!")

    await state.update_data(url=message.text)
    await state.set_state(BotStates.project_synonyms)
    await message.answer("Введите синонимы через запятую:")


@dp.message(BotStates.project_synonyms)
async def process_project_synonyms(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    synonyms = [s.strip() for s in message.text.split(",") if s.strip()]

    try:
        project_id = await add_project_to_db(
            name=data["name"], url=data["url"], synonyms=synonyms
        )
        await message.answer(f"✅ Проект '{data['name']}' добавлен (ID: {project_id})")
    except Exception as e:
        logger.error(f"Ошибка при добавлении проекта: {e}")
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()


@dp.message(F.text == "Удалить проект")
async def delete_project_start(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Доступ запрещен!")

    projects = await get_all_projects()
    if not projects:
        return await message.answer("❌ Нет проектов для удаления")

    keyboard = types.InlineKeyboardMarkup()
    for p in projects:
        keyboard.add(
            types.InlineKeyboardButton(
                text=p['name'], callback_data=f"delete_{p['id']}"
            )
        )
    await message.answer("Выберите проект:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data and c.data.startswith("delete_"))
async def delete_project_confirm(callback: types.CallbackQuery) -> None:
    project_id = int(callback.data.split("_")[1])
    try:
        await delete_project_from_db(project_id)
        await callback.message.edit_text("✅ Проект удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении проекта: {e}")
        await callback.message.edit_text(f"❌ Ошибка: {e}")


@dp.message()
async def handle_search(message: types.Message) -> None:
    query = message.text.strip()
    logger.debug(f"Пользователь {message.from_user.id} запросил: '{query}'")

    try:
        results = await search_projects(query)
        if not results:
            return await message.answer("Ничего не найдено 😔")

        response = "🔍 Результаты поиска:\n" + "\n".join(
            f"• {r['name']}: {r['url']}" for r in results
        )
        await message.answer(response)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}", exc_info=True)
        await message.answer("⚠️ Произошла ошибка при поиске")


async def main() -> None:
    if not await check_db_connection():
        logger.critical("Не удалось подключиться к базе данных")
        return

    logger.info("🟢 Бот запущен")
    bot = Bot(token=BOT_TOKEN)
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("🔴 Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
