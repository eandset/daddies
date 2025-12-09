from dataclasses import dataclass, field, asdict
from typing import Optional, Set, Dict, Any
import json


@dataclass
class Preference:
    events: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Preference':
        """Создание Preference из словаря"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class User:
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_chats: Set[int] = field(default_factory=set)
    preferences: Preference = field(default_factory=Preference)
    location: Optional[str] = None
    notification: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь с поддержкой вложенных dataclasses"""
        data = asdict(self)
        # Преобразуем set в list для JSON-совместимости
        if self.user_chats is not None:
            data['user_chats'] = list(self.user_chats)
        return data

    def to_json(self) -> str:
        """Конвертация в JSON строку"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создание User из словаря"""
        # Обрабатываем вложенный preference
        if 'preference' in data and isinstance(data['preference'], dict):
            data['preference'] = Preference.from_dict(data['preference'])

        # Обрабатываем user_chats (может быть list в JSON)
        if 'user_chats' in data:
            if isinstance(data['user_chats'], list):
                data['user_chats'] = set(data['user_chats'])
            elif data['user_chats'] is None:
                data['user_chats'] = set()

        # Убираем лишние ключи
        valid_keys = {f.name for f in field(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)

    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Создание User из JSON строки"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __post_init__(self):
        """Проверка после инициализации"""
        if self.user_chats is None:
            self.user_chats = set()
        if self.preferences is None:
            self.preference = Preference()


@dataclass
class Chat:
    chat_id: Optional[int] = None
    user_ids: Set[int] = field(default_factory=set)

    def __post_init__(self):
        if self.user_ids is None:
            self.user_ids = set()