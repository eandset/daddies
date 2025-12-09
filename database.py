from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SimpleDatabase:
    """Мок-класс базы данных для работы в памяти"""

    def __init__(self):
        self.users_data = {}
        self.feedbacks = []
        logger.info("Инициализирована мок-база данных в памяти")

    def get_or_create_user(self, user_id, first_name="", last_name=""):
        """Создает или получает пользователя"""
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                'vk_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'city': None,
                'eco_score': 0,
                'level': 1,
                'registration_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'tips_viewed': 0,
                'actions': []
            }
            logger.info(f"Создан новый пользователь: {user_id}")

        return self.users_data[user_id]

    def update_user_city(self, user_id, city):
        """Обновляет город пользователя"""
        if user_id in self.users_data:
            self.users_data[user_id]['city'] = city
            self.add_user_action(user_id, 'set_city', 10, f"Установлен город: {city}")
            return True
        return False

    def add_user_action(self, user_id, action_type, points, description=""):
        """Добавляет действие пользователя"""
        if user_id in self.users_data:
            action = {
                'type': action_type,
                'points': points,
                'description': description,
                'timestamp': datetime.now().strftime('%d.%m.%Y %H:%M')
            }
            self.users_data[user_id]['actions'].append(action)
            self.users_data[user_id]['eco_score'] += points

            # Проверка повышения уровня (каждые 100 баллов)
            new_level = self.users_data[user_id]['eco_score'] // 100 + 1
            if new_level > self.users_data[user_id]['level']:
                self.users_data[user_id]['level'] = new_level

            return True
        return False

    def add_feedback(self, user_id, text, rating=None):
        """Добавляет отзыв"""
        feedback = {
            'user_id': user_id,
            'text': text,
            'rating': rating,
            'timestamp': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        self.feedbacks.append(feedback)
        logger.info(f"Добавлен отзыв от пользователя {user_id}")
        return True

    def get_top_users(self, limit=10):
        """Возвращает топ пользователей по баллам"""
        users_list = list(self.users_data.values())
        sorted_users = sorted(users_list, key=lambda x: x['eco_score'], reverse=True)
        return sorted_users[:limit]

    def get_user_stats(self, user_id):
        """Возвращает статистику пользователя"""
        if user_id in self.users_data:
            user = self.users_data[user_id]
            return {
                'score': user['eco_score'],
                'level': user['level'],
                'city': user['city'],
                'tips_viewed': user['tips_viewed'],
                'actions_count': len(user['actions']),
                'registration_date': user['registration_date']
            }
        return None

    def save_state(self):
        """Сохраняет состояние (заглушка для будущей реализации)"""
        logger.info(f"Текущее состояние: {len(self.users_data)} пользователей, {len(self.feedbacks)} отзывов")
        return {
            'users_count': len(self.users_data),
            'feedbacks_count': len(self.feedbacks),
            'total_score': sum(user['eco_score'] for user in self.users_data.values())
        }