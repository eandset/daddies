vk_token=""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Токен ВК из переменных окружения
    VK_TOKEN = os.getenv('VK_TOKEN', 'vk1.a.e0gXIlAOeoDFpNkkUrnZEu2ctKjZbAowpZd8JoToQmRMO_xEluC9p7zdLzoVgjgLt5eh-E5LUzpwz3URFmVk41MqKMAZdBcw2BGRB1ltlPFf6mf6DP-KQOmarnRhrCKJxvpoYG2nFafCkFYI-BIciHbltJ8vO9yLEgouBaO6qUR3XseSFyTL8BpSZTW-VHISXwdvPf3J_85QFHwATCmUng')
    GROUP_ID = int(os.getenv('GROUP_ID', 0))

    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'eco_bot_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # API ключи для интеграций (будут добавлены позже)
    YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY', '')
    OPENSTREETMAP_API_KEY = os.getenv('OPENSTREETMAP_API_KEY', '')

    # Настройки приложения
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ADMIN_IDS = [int(id_) for id_ in os.getenv('ADMIN_IDS', '').split(',') if id_]

    # Настройки уведомлений
    NOTIFICATION_HOUR = 10  # Время отправки ежедневных уведомлений

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


config = Config()