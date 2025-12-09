import json
from typing import List, Optional, Dict, Any, Set

import sqlite3, aiosqlite


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._create_table_users()

    def _create_table_users(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    user_chats TEXT,
                    preferences = TEXT,
                    location = TEXT
                    notification INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    async def save_user(self, user_id: int, user_name: str, user_chats: set,
                        perferences: List[bool], location: str, notification: bool):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users
                (user_id, user_name, user_chats, perferences, location, notification) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, json.dumps(list(user_chats)),
                  json.dumps(map(int, perferences)), location, int(notification)))
            await db.commit()


    async def get_user(self, user_id: int, *fields: str) -> Optional[Dict[str, Any]]:
        '''
        Доступные поля:
        user_id, user_name, user_chats, preferences, location, notification
        '''
        if not fields:
            fields = ("user_id", "user_name", "user_chats", "preferences",
                      "location", "notification")

        allowed_fields = {"user_id", "user_name", "user_chats", "preferences",
                          "location", "notification", "created_at", "updated_at"}
        for field in fields:
            if field not in allowed_fields:
                raise ValueError(f"Поле '{field}' не существует в таблице users")

        fields_str = ", ".join(fields)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    f"SELECT {fields_str} FROM users WHERE user_id = ?",
                    (user_id,)
            ) as cursor:
                result = await cursor.fetchone()

                if result:
                    data = {}
                    for i, field in enumerate(fields):
                        value = result[i]

                        if field in ["user_chats", "preferences"] and value:
                            try:
                                data[field] = json.loads(value)
                            except (json.JSONDecodeError, TypeError):
                                data[field] = value
                        else:
                            data[field] = value

                    return data
                return None

