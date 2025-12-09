import json
from typing import Union, Optional, Dict, Any, Set
import sqlite3
import aiosqlite
from models import Chat, User, Preference


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._create_table_users()
        self._create_table_chats()

    def _create_table_users(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    user_chats TEXT DEFAULT '[]',
                    preferences TEXT DEFAULT '{}',
                    location TEXT DEFAULT '',
                    notification INTEGER DEFAULT 0,
                )
            ''')
            conn.commit()

    def _create_table_chats(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    user_ids TEXT DEFAULT '[]'
                )
            ''')
            conn.commit()

    async def save_user(self, user: User):
        '''Обновить данные пользователя в бд'''
        user_dict = user.to_dict()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, user_name, user_chats, preferences, location, notification, page)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_dict['user_id'],
                user_dict['user_name'],
                json.dumps(user_dict['user_chats']),
                json.dumps(user_dict['preferences']),
                user_dict['location'],
                int(user_dict.get('notification', True))
            ))
            await db.commit()
            return True

    async def get_user(self, user_id: int, *fields: str) -> Union[Optional[Dict[str, Any]], User]:
        """
        Получение данных пользователя в виде словаря

        Args:
            user_id: ID пользователя
            *fields: поля для получения (если пусто - экземпляр класса User)

        Returns:
            Словарь с данными, экземпляр класса User или None, если пользователь не найден
        """
        # Определяем, нужно ли возвращать объект User
        return_object = len(fields) == 0

        # Если поля не указаны - получаем все для объекта User
        if return_object:
            fields = ("user_id", "user_name", "user_chats", "preferences",
                      "location", "notification", "page")

        allowed_fields = {"user_id", "user_name", "user_chats", "preferences",
                          "location", "notification", "page"}

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

                if not result:
                    return None

                # Собираем данные в словарь
                data = {}
                for i, field in enumerate(fields):
                    value = result[i]

                    # Десериализация JSON полей
                    if field in ["user_chats", "preferences"] and value:
                        try:
                            data[field] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            data[field] = value
                    else:
                        data[field] = value

                # Если запросили объект User - создаем его
                if return_object:
                    # Преобразуем список user_chats в set
                    if 'user_chats' in data:
                        data['user_chats'] = set(data['user_chats'])

                    # Создаем объект Preference из словаря
                    if 'preferences' in data and isinstance(data['preferences'], dict):
                        data['preferences'] = Preference(**data['preferences'])

                    return User(**data)

                return data

    async def get_all_users(self) -> Dict[int, User]:
        """
        Получить словарь всех пользователей.

        Returns:
            Словарь вида {user_id: User}
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT user_id, user_name, user_chats, preferences, location, notification, page FROM users"
            ) as cursor:
                users = {}

                async for row in cursor:
                    user_id, user_name, user_chats_json, prefs_json, location, notification, page = row

                    # Десериализация JSON полей
                    user_data = {
                        'user_id': user_id,
                        'user_name': user_name,
                        'location': location,
                        'notification': bool(notification),
                        'page': bool(page)
                    }

                    try:
                        user_data['user_chats'] = json.loads(user_chats_json) if user_chats_json else []
                    except json.JSONDecodeError:
                        user_data['user_chats'] = []

                    try:
                        user_data['preferences'] = json.loads(prefs_json) if prefs_json else {}
                    except json.JSONDecodeError:
                        user_data['preferences'] = {}

                    users[user_id] = User.from_dict(user_data)

                return users

    async def save_chat(self, chat: Chat):
        '''Обновить данные чата в бд'''
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO chats
                (chat_id, user_ids) 
                VALUES (?, ?)
            ''', (
                chat.chat_id,
                json.dumps(list(chat.user_ids))
            ))
            await db.commit()
            return True

    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        '''Получить чат как объект Chat'''
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT chat_id, user_ids FROM chats WHERE chat_id = ?",
                    (chat_id,)
            ) as cursor:
                result = await cursor.fetchone()

                if result:
                    chat_id, user_ids_json = result
                    try:
                        user_ids = set(json.loads(user_ids_json)) if user_ids_json else set()
                        return Chat(chat_id=chat_id, user_ids=user_ids)
                    except json.JSONDecodeError:
                        return Chat(chat_id=chat_id, user_ids=set())
                return None

    async def get_all_chats(self) -> Dict[int, Chat]:
        """
        Получить словарь всех чатов.

        Returns:
            Словарь вида {chat_id: Chat}
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT chat_id, user_ids FROM chats"
            ) as cursor:
                chats = {}

                async for row in cursor:
                    chat_id, user_ids_json = row

                    try:
                        user_ids = json.loads(user_ids_json) if user_ids_json else []
                    except json.JSONDecodeError:
                        user_ids = []

                    chats[chat_id] = Chat(chat_id, user_ids)

                return chats