import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def get_db_connection():
    return await asyncpg.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host="localhost")

