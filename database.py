import os
import asyncpg
from dotenv import load_dotenv
from loguru import logger

# Загрузка переменных окружения
load_dotenv()


async def get_db_connection() -> asyncpg.Connection:
    """Создает подключение к PostgreSQL"""
    return await asyncpg.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host="db" if os.getenv("DOCKER_MODE") else "localhost"
    )


async def check_db_connection() -> bool:
    """Проверка подключения к базе данных"""
    try:
        conn = await get_db_connection()
        await conn.close()
        logger.success("Подключение к PostgreSQL успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения: {str(e)}")
        return False


async def search_projects(query: str) -> list:
    """Поиск проектов по названию и синонимам"""
    conn = None
    try:
        conn = await get_db_connection()
        logger.debug(f"Выполнение запроса для: '{query}'")

        results = await conn.fetch(
            """
            SELECT p.name, p.url 
            FROM projects p
            LEFT JOIN synonyms s ON p.id = s.project_id
            WHERE p.name ILIKE $1 OR s.synonym ILIKE $1
            """,
            f"%{query}%"
        )

        return results

    except Exception as e:
        logger.error(f"Ошибка SQL-запроса: {str(e)}")
        return []
    finally:
        if conn: await conn.close()