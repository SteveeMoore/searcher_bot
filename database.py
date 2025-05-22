import os
from typing import List, Dict, Any
import asyncpg
from dotenv import load_dotenv
from loguru import logger

# Загрузка переменных окружения
load_dotenv()

DB_CONFIG = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB'),
    'host': 'db' if os.getenv('DOCKER_MODE', 'false').lower() == 'true' else 'localhost',
}


async def get_db_connection() -> asyncpg.Connection:
    """Создает подключение к PostgreSQL"""
    return await asyncpg.connect(**DB_CONFIG)


async def check_db_connection() -> bool:
    """Проверка подключения к базе данных"""
    try:
        conn = await get_db_connection()
        await conn.close()
        logger.success("Подключение к PostgreSQL успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return False


async def add_project_to_db(name: str, url: str, synonyms: List[str]) -> int:
    conn = await get_db_connection()
    try:
        project = await conn.fetchrow(
            "INSERT INTO projects (name, url) VALUES ($1, $2) RETURNING id",
            name, url,
        )
        project_id = project['id']

        if synonyms:
            values = [(project_id, syn) for syn in synonyms]
            await conn.executemany(
                "INSERT INTO synonyms (project_id, synonym) VALUES ($1, $2)",
                values,
            )

        return project_id
    except Exception as e:
        logger.error(f"DB Error (add_project): {e}")
        raise
    finally:
        await conn.close()


async def get_all_projects() -> List[Dict[str, Any]]:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("SELECT id, name FROM projects ORDER BY name")
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def delete_project_from_db(project_id: int) -> None:
    conn = await get_db_connection()
    try:
        await conn.execute("DELETE FROM projects WHERE id = $1", project_id)
    finally:
        await conn.close()


async def search_projects(query: str) -> List[Dict[str, Any]]:
    """Поиск проектов по названию и синонимам"""
    conn = await get_db_connection()
    try:
        pattern = f"%{query}%"
        rows = await conn.fetch(
            """
            SELECT DISTINCT p.name, p.url
            FROM projects p
            LEFT JOIN synonyms s ON p.id = s.project_id
            WHERE p.name ILIKE $1 OR s.synonym ILIKE $1
            ORDER BY p.name
            """,
            pattern,
        )
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"DB Error (search_projects): {e}")
        return []
    finally:
        await conn.close()