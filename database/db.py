import aiosql
import aiosqlite
from typing import Optional

class Database:
    def __init__(self, db_path: str, sql_path: str):
        self.db_path = db_path
        self.queries = aiosql.from_path(sql_path, "aiosqlite")
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row # Чтобы обращаться к полям по имени
        await self.queries.create_schema(self.conn)
        await self.conn.commit()
        print("📁 База данных подключена")

    async def close(self):
        if self.conn:
            await self.conn.close()

# Инициализация (Singleton-like для простоты)
db = Database("eco_bot.db", "sql/")