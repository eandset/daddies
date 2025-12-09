from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseHandler(ABC):
    """Базовый класс для всех обработчиков сообщений"""

    def __init__(self, vk_api, db, user_id):
        self.vk_api = vk_api
        self.db = db
        self.user_id = user_id

    @abstractmethod
    async def handle(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        Обрабатывает сообщение пользователя
        Возвращает словарь с результатом обработки
        """
        pass

    def send_message(self, text: str, keyboard=None):
        """Отправляет сообщение пользователю"""
        params = {
            'user_id': self.user_id,
            'message': text,
            'random_id': 0
        }
        if keyboard:
            params['keyboard'] = keyboard.get_keyboard()

        self.vk_api.messages.send(**params)