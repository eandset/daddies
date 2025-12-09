import logging
import random
import re
from vk_api.utils import get_random_id
from database import SimpleDatabase
from keyboards import Keyboards
from config import config
from maps_service import maps_service

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик входящих сообщений"""

    def __init__(self, vk_api):
        self.vk_api = vk_api
        self.db = SimpleDatabase()
        self.commands = self._get_commands_list()
        self.user_states = {}  # Для отслеживания состояний пользователей

    def _get_commands_list(self):
        """Возвращает список всех команд"""
        return {
            'start': 'Начать работу с ботом',
            'help': 'Показать список команд',
            'profile': 'Мой профиль и статистика',
            'points': 'Пункты приёма вторсырья по городу',
            'events': 'Ближайшие эко-события',
            'tips': 'Случайный эко-совет',
            'rating': 'Рейтинг активности',
            'feedback': 'Оставить отзыв о боте',
            'settings': 'Настройки бота',
            'город [название]': 'Указать свой город для поиска',
            'рядом': 'Найти пункты приема по геолокации',
            'локация': 'Отправить свое местоположение',
            'где я': 'Найти пункты приема рядом'
        }

    def send_message(self, user_id, text, keyboard=None, attachment=None):
        """Отправляет сообщение пользователю"""
        params = {
            'user_id': user_id,
            'message': text,
            'random_id': get_random_id(),
        }

        if keyboard:
            params['keyboard'] = keyboard
        else:
            # Используем главную клавиатуру по умолчанию
            params['keyboard'] = Keyboards.get_main_keyboard()

        if attachment:
            params['attachment'] = attachment

        try:
            self.vk_api.messages.send(**params)
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def handle_message(self, user_id, message, first_name="", last_name="", attachments=None):
        """Основной метод обработки сообщения"""
        message_lower = message.lower().strip()

        # Логируем вложения для отладки
        if attachments:
            logger.info(f"Вложения от {user_id}: {attachments}")

        # Проверяем, есть ли вложения с геолокацией
        geo_data = self._extract_geo_from_attachments(attachments)
        if geo_data:
            logger.info(f"Найдена геолокация от {user_id}: {geo_data}")
            return self._handle_geo_data(user_id, geo_data, first_name)

        # Проверяем состояние пользователя
        if user_id in self.user_states and self.user_states[user_id].get('waiting_for_location'):
            return self._handle_location_response(user_id, message, first_name)

        # Обработка команд
        if message_lower in ['привет', 'start', 'начать', 'старт', 'hello', 'hi']:
            return self._handle_start(user_id, first_name)
        elif message_lower in ['помощь', 'help', 'команды', 'справка']:
            return self._handle_help(user_id)
        elif message_lower in ['профиль', 'profile', 'статистика', 'мой профиль']:
            return self._handle_profile(user_id)
        elif 'пункт' in message_lower or 'points' in message_lower or 'приём' in message_lower:
            return self._handle_city_points(user_id, message)
        elif 'рядом' == message_lower or 'ближайшие' in message_lower or 'где я' in message_lower:
            return self._handle_nearby_request(user_id)
        elif 'локация' in message_lower or 'местоположение' in message_lower or 'гео' in message_lower:
            return self._handle_location_request(user_id)
        elif 'события' in message_lower or 'events' in message_lower or 'мероприятия' in message_lower:
            return self._handle_events(user_id)
        elif 'совет' in message_lower or 'tips' in message_lower or 'подсказка' in message_lower:
            return self._handle_tips(user_id)
        elif 'рейтинг' in message_lower or 'rating' in message_lower or 'топ' in message_lower:
            return self._handle_rating(user_id)
        elif 'отзыв' in message_lower or 'feedback' in message_lower:
            return self._handle_feedback(user_id, message)
        elif 'город' in message_lower:
            return self._handle_city(user_id, message)
        elif 'настройки' in message_lower or 'settings' in message_lower:
            return self._handle_settings(user_id)
        elif message_lower in ['спасибо', 'thanks', 'благодарю']:
            return self._handle_thanks(user_id)
        elif message_lower in ['о боте', 'about', 'информация']:
            return self._handle_about(user_id)
        elif 'карта' in message_lower or 'map' in message_lower:
            return self._handle_map_info(user_id)

        # Если команда не распознана
        return self._handle_unknown(user_id, message)

    def _extract_geo_from_attachments(self, attachments):
        """Извлекает геоданные из вложений ВК"""
        if not attachments:
            return None

        try:
            logger.info(f"Анализ вложений: {attachments}")

            # Если это строка, пытаемся найти гео-данные
            if isinstance(attachments, str):
                # Ищем гео в строке
                if 'geo' in attachments.lower():
                    # Это может быть закодированная геолокация ВК
                    geo_match = re.search(r'"geo":"([^"]+)"', attachments)
                    if geo_match:
                        geo_code = geo_match.group(1)
                        logger.info(f"Найден гео-код ВК: {geo_code}")
                        return {'type': 'vk_geo_code', 'code': geo_code}

                    # Ищем координаты в формате lat_lon
                    coord_match = re.search(r'(-?\d+\.\d+)_(-?\d+\.\d+)', attachments)
                    if coord_match:
                        lat = float(coord_match.group(1))
                        lon = float(coord_match.group(2))
                        logger.info(f"Найдены координаты в строке: {lat}, {lon}")
                        return {'type': 'coordinates', 'lat': lat, 'lon': lon}

            # Если это словарь
            elif isinstance(attachments, dict):
                if 'geo' in attachments:
                    geo_value = attachments['geo']
                    logger.info(f"Гео из словаря: {geo_value}")

                    if isinstance(geo_value, str):
                        # Пытаемся найти координаты
                        coord_match = re.search(r'(-?\d+\.\d+)_(-?\d+\.\d+)', geo_value)
                        if coord_match:
                            lat = float(coord_match.group(1))
                            lon = float(coord_match.group(2))
                            return {'type': 'coordinates', 'lat': lat, 'lon': lon}
                        else:
                            # Это код ВК
                            return {'type': 'vk_geo_code', 'code': geo_value}

            logger.warning(f"Не удалось извлечь геоданные из: {attachments}")
            return None

        except Exception as e:
            logger.error(f"Ошибка извлечения геоданных: {e}")
            return None

    def _handle_geo_data(self, user_id, geo_data, first_name=""):
        """Обработка полученных геоданных"""
        try:
            # Сбрасываем состояние ожидания
            if user_id in self.user_states:
                self.user_states[user_id]['waiting_for_location'] = False

            # В зависимости от типа геоданных
            if geo_data['type'] == 'coordinates':
                # У нас есть прямые координаты
                lat = geo_data['lat']
                lon = geo_data['lon']
                location_name = f"координаты {lat:.4f}, {lon:.4f}"

                logger.info(f"Обработка координат: {lat}, {lon}")
                return self._search_points_by_coordinates(user_id, lat, lon, first_name, location_name)

            elif geo_data['type'] == 'vk_geo_code':
                # Это код геолокации ВК
                logger.info(f"Получение координат по коду ВК: {geo_data['code']}")

                self.send_message(
                    user_id,
                    "📍 *Я получил твою геолокацию от ВК!*\n\n"
                    "Для точного поиска мне нужны координаты.\n\n"
                    "*Пожалуйста, сделай так:*\n"
                    "1. Нажми на скрепку 📎 еще раз\n"
                    "2. Выбери 'Геолокация' или 'Местоположение'\n"
                    "3. На карте нажми 'Отправить текущее местоположение'\n"
                    "4. Или выбери точку на карте вручную\n\n"
                    "Или напиши адрес места, где ты находишься."
                )

                # Устанавливаем состояние ожидания
                self.user_states[user_id] = {'waiting_for_location': True}

                return {'success': True, 'action': 'vk_geo_received'}

            else:
                logger.error(f"Неизвестный тип геоданных: {geo_data}")
                self.send_message(
                    user_id,
                    "❌ *Не удалось распознать формат геолокации.*\n\n"
                    "Пожалуйста, отправь геолокацию еще раз:\n"
                    "1. Нажми на скрепку 📎\n"
                    "2. Выбери 'Геолокация'\n"
                    "3. Выбери 'Отправить текущее местоположение'\n\n"
                    "Или напиши адрес, где ты находишься."
                )
                return {'success': False, 'action': 'unknown_geo_format'}

        except Exception as e:
            logger.error(f"Ошибка обработки геоданных: {e}")
            self.send_message(
                user_id,
                "😔 Произошла ошибка при обработке местоположения.\n"
                "Попробуй отправить геолокацию еще раз или напиши адрес."
            )
            return {'success': False, 'action': 'geo_processing_error'}

    def _handle_nearby_request(self, user_id):
        """Запрос на поиск ближайших пунктов"""
        keyboard = Keyboards.get_location_keyboard()

        request_text = (
            "📍 *Найду пункты приема рядом с тобой!*\n\n"
            "*Есть 3 способа:*\n\n"
            "1. 📎 *Отправь геолокацию:*\n"
            "   • Нажми на скрепку рядом с полем ввода\n"
            "   • Выбери 'Геолокация' или 'Местоположение'\n"
            "   • Нажми 'Отправить текущее местоположение'\n\n"
            "2. 📍 *Используй кнопку ниже* (если поддерживается)\n\n"
            "3. 🏠 *Напиши адрес:*\n"
            "   Например: 'ул. Ленина, 15' или 'метро Китай-город'\n\n"
            "Выбери удобный способ! 👇"
        )

        # Устанавливаем состояние ожидания
        self.user_states[user_id] = {'waiting_for_location': True}

        self.send_message(user_id, request_text, keyboard)
        return {'success': True, 'action': 'request_location'}

    def _handle_location_request(self, user_id):
        """Обработка команды запроса локации"""
        return self._handle_nearby_request(user_id)

    def _handle_location_response(self, user_id, message, first_name=""):
        """Обработка ответа пользователя после запроса локации"""
        message_lower = message.lower().strip()

        # Сбрасываем состояние
        if user_id in self.user_states:
            self.user_states[user_id]['waiting_for_location'] = False

        if message_lower in ['отмена', 'cancel', 'стоп', 'нет']:
            self.send_message(user_id, "❌ Поиск по местоположению отменен.")
            return {'success': False, 'action': 'location_search_cancelled'}

        # Если пользователь написал адрес или место
        if message_lower and message_lower not in ['да', 'ок', 'хорошо']:
            logger.info(f"Пользователь {user_id} указал место: {message}")

            self.send_message(
                user_id,
                f"🔍 *Ищу пункты приема рядом с '{message}'...*\n\n"
                "Используется геокодирование и OpenStreetMap."
            )

            try:
                # Пытаемся геокодировать введенное место
                geocode_result = maps_service.geocode_city(message)
                if geocode_result:
                    location_name = geocode_result.get('name', message)
                    return self._search_points_by_coordinates(
                        user_id,
                        geocode_result['lat'],
                        geocode_result['lon'],
                        first_name,
                        location_name=location_name
                    )
                else:
                    # Пробуем поискать как адрес
                    self.send_message(
                        user_id,
                        f"🔍 *Ищу '{message}' в OpenStreetMap...*"
                    )

                    points = self._search_by_address(message)
                    if points:
                        return self._show_points_from_search(user_id, points, message)
                    else:
                        self.send_message(
                            user_id,
                            f"❌ *Не удалось найти место '{message}'*\n\n"
                            "Попробуй:\n"
                            "• Отправить геолокацию через скрепку 📎\n"
                            "• Указать более точный адрес\n"
                            "• Написать название района или станции метро\n"
                            "• Использовать поиск по городу: 'город Москва'"
                        )
                        return {'success': False, 'action': 'location_not_found'}

            except Exception as e:
                logger.error(f"Ошибка поиска по месту '{message}': {e}")
                self.send_message(
                    user_id,
                    "😔 Произошла ошибка при поиске.\n"
                    "Попробуй отправить геолокацию или указать другой адрес."
                )
                return {'success': False, 'action': 'location_search_error'}

        # Если пользователь просто подтвердил
        keyboard = Keyboards.get_location_keyboard()
        self.send_message(
            user_id,
            "📍 *Отправь свою геолокацию для поиска!*\n\n"
            "Нажми на скрепку 📎 рядом с полем ввода\n"
            "→ Выбери 'Геолокация'\n"
            "→ Выбери 'Отправить текущее местоположение'\n\n"
            "Или используй кнопку ниже 👇",
            keyboard
        )
        return {'success': True, 'action': 'request_geo_again'}

    def _search_by_address(self, address):
        """Поиск пунктов приема по адресу"""
        try:
            geocode_result = maps_service.geocode_city(address)
            if not geocode_result:
                return []

            lat = geocode_result['lat']
            lon = geocode_result['lon']

            radius_m = 2000  # 2 км
            osm_data = maps_service.over_pass_query(lat, lon, radius_m)
            points = maps_service.parse_elements(osm_data)

            user_location = (lat, lon)
            nearest_points = maps_service.get_nearest_points(points, user_location, max_distance_km=2, limit=15)

            return nearest_points

        except Exception as e:
            logger.error(f"Ошибка поиска по адресу '{address}': {e}")
            return []

    def _show_points_from_search(self, user_id, points, location_name):
        """Показывает найденные точки"""
        if not points:
            self.send_message(
                user_id,
                f"❌ *В районе '{location_name}' не найдено пунктов приема.*\n\n"
                "Попробуй:\n"
                "• Отправить геолокацию для точного поиска\n"
                "• Указать другой адрес\n"
                "• Искать по городу"
            )
            return {'success': False, 'action': 'no_points_found'}

        points_message = maps_service.format_points_for_message(points)
        stats = maps_service.get_statistics(points)

        location_info = (
            f"\n📍 *Поиск по адресу:*\n"
            f"• Место: {location_name}\n"
            f"• Найдено объектов: {stats['total']}\n"
            f"• Среднее расстояние: {stats['avg_distance']} км\n\n"
        )

        full_message = location_info + points_message

        if len(full_message) > 3000:
            full_message = full_message[:2900] + "\n\n...[сообщение обрезано]"

        self.send_message(user_id, full_message)

        self.db.add_user_action(
            user_id,
            'search_by_address',
            20,
            f"Искал пункты по адресу '{location_name}', найдено {len(points)}"
        )

        return {'success': True, 'action': 'address_search_success', 'points_found': len(points)}

    def _search_points_by_coordinates(self, user_id, lat, lon, first_name="", location_name=None):
        """Поиск пунктов приема по координатам"""
        try:
            user = self.db.get_or_create_user(user_id, first_name, "")

            if not location_name:
                location_name = f"координаты {lat:.4f}, {lon:.4f}"

            search_text = (
                f"🔍 *Ищу пункты приема рядом с тобой...*\n\n"
                f"📍 Местоположение: {location_name}\n"
                f"📏 Радиус поиска: 2 км\n\n"
                f"Используются данные OpenStreetMap..."
            )
            self.send_message(user_id, search_text)

            radius_m = 2000
            osm_data = maps_service.over_pass_query(lat, lon, radius_m)
            points = maps_service.parse_elements(osm_data)
            user_location = (lat, lon)
            nearest_points = maps_service.get_nearest_points(points, user_location, max_distance_km=2, limit=15)

            if not nearest_points:
                no_points_text = (
                    f"❌ *В радиусе 2 км не найдено пунктов приема.*\n\n"
                    f"*Твое местоположение:* {location_name}\n\n"
                    f"*Попробуй:*\n"
                    f"1. Увеличить радиус поиска (укажи другой адрес)\n"
                    f"2. Проверить на картах 2GIS или Яндекс.Картах\n"
                    f"3. Узнать в местной администрации\n\n"
                    f"Или поищи по городу: 'город Москва'"
                )
                self.send_message(user_id, no_points_text)
                return {'success': False, 'action': 'no_points_nearby'}

            points_message = maps_service.format_points_for_message(nearest_points)
            stats = maps_service.get_statistics(nearest_points)

            location_info = (
                f"\n📍 *Поиск по местоположению:*\n"
                f"• Место: {location_name}\n"
                f"• Координаты: {lat:.4f}, {lon:.4f}\n"
                f"• Радиус: 2 км\n"
                f"• Найдено объектов: {len(nearest_points)}\n\n"
            )

            stats_message = (
                f"📊 *Статистика:*\n"
                f"• Среднее расстояние: {stats['avg_distance']} км\n"
            )

            if stats['closest']:
                stats_message += f"• Ближайший: {stats['closest']['distance_km']} км\n"

            full_message = location_info + points_message + stats_message

            if len(full_message) > 3000:
                full_message = full_message[:2900] + "\n\n...[сообщение обрезано]"

            self.send_message(user_id, full_message)

            self.db.add_user_action(
                user_id,
                'search_by_location',
                25,
                f"Искал пункты по координатам {lat:.4f}, {lon:.4f}, найдено {len(nearest_points)}"
            )

            advice_message = (
                "\n💡 *Советы для посещения:*\n"
                "1. Уточни часы работы по телефону\n"
                "2. Возьми с собой документ (паспорт)\n"
                "3. Подготовь отходы: вымой, отсортируй\n"
                "4. Используй многоразовые контейнеры\n\n"
                "Спасибо за заботу о природе! 🌍💚"
            )

            self.send_message(user_id, advice_message)

            user['last_location'] = {'lat': lat, 'lon': lon, 'name': location_name}

            return {
                'success': True,
                'action': 'location_search_success',
                'points_found': len(nearest_points),
                'location': {'lat': lat, 'lon': lon}
            }

        except Exception as e:
            logger.error(f"Ошибка поиска по координатам: {e}")
            self.send_message(
                user_id,
                "😔 *Произошла ошибка при поиске по местоположению.*\n\n"
                "Причины могут быть:\n"
                "1. Проблемы с картографическими данными\n"
                "2. Нет пунктов приема в этом районе\n"
                "3. Временные проблемы с сервисом\n\n"
                "Попробуй:\n"
                "• Отправить другую геолокацию\n"
                "• Указать город для поиска\n"
                "• Попробовать позже"
            )
            return {'success': False, 'action': 'location_search_error', 'error': str(e)}

    def _handle_start(self, user_id, first_name):
        """Обработка приветствия"""
        user = self.db.get_or_create_user(user_id, first_name, "")

        welcome_text = (
            f"Привет, {first_name}! 👋\n\n"
            f"Я - {config.BOT_NAME} ({config.BOT_VERSION})\n\n"
            f"Я помогу тебе:\n"
            f"• Найти ближайшие пункты приёма вторсырья ♻️\n"
            f"• Узнать об эко-событиях 🌿\n"
            f"• Получить полезные советы\n"
            f"• Отслеживать эко-активность\n\n"
            f"*Новые функции:*\n"
            f"📍 Поиск по городу (команда 'город Москва')\n"
            f"📍 Поиск по твоему местоположению (команда 'где я')\n"
            f"📍 Отправь геолокацию для точного поиска рядом\n\n"
            f"Используй кнопки ниже или напиши 'помощь'."
        )

        self.db.add_user_action(user_id, 'start', 5, "Начал работу с ботом")

        # Явно указываем клавиатуру
        self.send_message(user_id, welcome_text, Keyboards.get_main_keyboard())
        return {'success': True, 'action': 'start'}

    def _handle_help(self, user_id):
        """Показывает список команд"""
        help_text = "📋 *Доступные команды:*\n\n"

        for cmd, desc in self.commands.items():
            help_text += f"• *{cmd}* - {desc}\n"

        help_text += "\n*Способы поиска пунктов приема:*\n"
        help_text += "1️⃣ `город Москва` → `пункты` - поиск по городу\n"
        help_text += "2️⃣ `где я` - запросить отправку местоположения\n"
        help_text += "3️⃣ 📎 Отправить геолокацию через скрепку - мгновенный поиск\n\n"
        help_text += "*Примеры:*\n"
        help_text += "`отзыв Отличный бот!` - оставить отзыв\n"
        help_text += "`совет` - получить эко-совет\n\n"
        help_text += "Используй кнопки меню ниже! 👇"

        self.send_message(user_id, help_text)
        return {'success': True, 'action': 'help'}

    def _handle_profile(self, user_id):
        """Показывает профиль пользователя"""
        user = self.db.get_or_create_user(user_id, "", "")
        stats = self.db.get_user_stats(user_id)

        if not stats:
            self.send_message(user_id, "❌ Ошибка загрузки профиля")
            return {'success': False, 'action': 'profile_error'}

        profile_text = (
            f"👤 *Твой профиль:*\n\n"
            f"*Имя:* {user['first_name']} {user.get('last_name', '')}\n"
            f"*Город:* {user['city'] or 'не указан'}\n"
            f"*Эко-рейтинг:* {stats['score']} баллов\n"
            f"*Уровень:* {stats['level']}\n"
            f"*Просмотрено советов:* {stats['tips_viewed']}\n"
            f"*Выполнено действий:* {stats['actions_count']}\n"
            f"*Зарегистрирован:* {stats['registration_date']}\n\n"
        )

        if 'last_location' in user:
            loc = user['last_location']
            profile_text += f"*Последний поиск по локации:*\n"
            profile_text += f"📍 {loc.get('name', 'Неизвестно')}\n"
            profile_text += f"📌 Координаты: {loc['lat']:.4f}, {loc['lon']:.4f}\n\n"

        recent_actions = user.get('actions', [])[-3:]
        if recent_actions:
            profile_text += "*Последние действия:*\n"
            for action in recent_actions:
                profile_text += f"• {action['description']} (+{action['points']} баллов)\n"

        profile_text += f"\n*Способы поиска:*\n• `город Москва` - по городу\n• `где я` - по местоположению\n• 📎 Отправь геолокацию"

        self.send_message(user_id, profile_text, Keyboards.get_profile_keyboard())
        return {'success': True, 'action': 'profile'}

    def _handle_city_points(self, user_id, message):
        """Поиск пунктов приёма по городу"""
        user = self.db.get_or_create_user(user_id, "", "")

        if not user['city']:
            keyboard = Keyboards.get_location_or_city_keyboard()

            self.send_message(
                user_id,
                "📍 *Выбери способ поиска пунктов приема:*\n\n"
                "1. *По городу* - укажи город для поиска\n"
                "2. *По местоположению* - отправь геолокацию\n\n"
                "Напиши 'город Москва' или отправь геолокацию 📎",
                keyboard
            )
            return {'success': False, 'action': 'choose_search_method'}

        self.send_message(
            user_id,
            f"🔍 *Ищу пункты приема в городе {user['city']}...*\n\n"
            "Используется OpenStreetMap - база открытых картографических данных."
        )

        try:
            points = maps_service.get_points_by_city(user['city'], radius_km=3)

            if not points:
                self.send_message(
                    user_id,
                    f"❌ *В городе {user['city']} не найдено пунктов приема.*\n\n"
                    "Попробуй:\n"
                    "1. Уточнить название города\n"
                    "2. Отправить геолокацию для точного поиска\n"
                    "3. Проверить вручную на картах"
                )
                return {'success': False, 'action': 'no_points_found'}

            points_message = maps_service.format_points_for_message(points)
            stats = maps_service.get_statistics(points)

            stats_message = (
                f"\n📊 *Статистика поиска в {user['city']}:*\n"
                f"• Найдено объектов: {stats['total']}\n"
                f"• Среднее расстояние: {stats['avg_distance']} км\n"
            )

            full_message = points_message + stats_message

            if len(full_message) > 3000:
                full_message = full_message[:2900] + "\n\n...[сообщение обрезано]"

            self.send_message(user_id, full_message)

            self.db.add_user_action(
                user_id,
                'search_city_points',
                15,
                f"Искал пункты в {user['city']}, найдено {len(points)}"
            )

            keyboard = Keyboards.get_location_keyboard()
            advice_message = (
                "\n💡 *Хочешь найти ближайшие к тебе пункты?*\n"
                "Отправь свою геолокацию 📎 для поиска в радиусе 2 км!\n"
                "Или нажми кнопку ниже 👇"
            )

            self.send_message(user_id, advice_message, keyboard)

            return {'success': True, 'action': 'city_points_search', 'points_found': len(points)}

        except Exception as e:
            logger.error(f"Ошибка поиска пунктов приема: {e}")
            self.send_message(
                user_id,
                "😔 *Произошла ошибка при поиске пунктов приема.*\n\n"
                "Попробуй отправить геолокацию для точного поиска рядом."
            )
            return {'success': False, 'action': 'points_search_error'}

    def _handle_events(self, user_id):
        """Показывает ближайшие эко-события"""
        user = self.db.get_or_create_user(user_id, "", "")

        events_text = "📅 *Ближайшие эко-события:*\n\n"

        events = getattr(config, 'ECO_EVENTS', [
            "🌱 Субботник в парке - завтра 10:00",
            "♻️ Мастер-класс по сортировке - послезавтра 18:00",
            "🌿 Лекция 'Экология города' - суббота 15:00",
            "🎯 Квест 'Чистый город' - воскресенье 12:00",
            "📚 Вебинар 'Zero Waste' - среда 19:00"
        ])

        for i, event in enumerate(events[:5], 1):
            events_text += f"{i}. {event}\n"

        if user['city']:
            events_text += f"\n*В твоём городе ({user['city']}) скоро:*\n"
            events_text += "🔜 Информация о локальных событиях появится позже!\n"

        events_text += "\n*Укажи город для точных событий:*\n"
        events_text += "Напиши: `город Москва`"

        self.db.add_user_action(user_id, 'view_events', 2, "Смотрел события")

        self.send_message(user_id, events_text)
        return {'success': True, 'action': 'events_list'}

    def _handle_tips(self, user_id):
        """Даёт случайный эко-совет"""
        eco_tips = getattr(config, 'ECO_TIPS', [
            "♻️ Сдавай вторсырье в найденные пункты приема",
            "🗺️ Используй карту для поиска ближайших эко-точек",
            "📱 Сохраняй адреса пунктов приема в заметки",
            "👥 Расскажи друзьям о найденных пунктах приема"
        ])

        tip = random.choice(eco_tips)
        user = self.db.get_or_create_user(user_id, "", "")

        user['tips_viewed'] += 1
        self.db.add_user_action(user_id, 'view_tip', 5, "Посмотрел эко-совет")

        tips_text = (
            f"🌿 *Эко-совет дня:*\n\n"
            f"{tip}\n\n"
            f"+5 баллов к рейтингу! 🎉\n"
            f"*Просмотрено советов:* {user['tips_viewed']}\n\n"
            f"Пиши `совет` для нового совета!\n"
            f"Каждый совет делает планету чище! 🌍"
        )

        self.send_message(user_id, tips_text)
        return {'success': True, 'action': 'daily_tip'}

    def _handle_rating(self, user_id):
        """Показывает рейтинг активности"""
        user = self.db.get_or_create_user(user_id, "", "")
        top_users = self.db.get_top_users(limit=10)

        rating_text = "🏆 *Топ эко-активистов:*\n\n"

        for i, top_user in enumerate(top_users, 1):
            name = top_user['first_name'][:10] if top_user['first_name'] else f"User{top_user['vk_id']}"
            city = f" ({top_user['city']})" if top_user['city'] else ""
            highlight = "➡️ " if top_user['vk_id'] == user_id else ""
            rating_text += f"{i}. {highlight}*{name}*{city}: {top_user['eco_score']} баллов\n"

        user_position = None
        for i, top_user in enumerate(top_users, 1):
            if top_user['vk_id'] == user_id:
                user_position = i
                break

        if user_position:
            rating_text += f"\n*Твоя позиция:* {user_position}\n"
        else:
            rating_text += f"\n*Твои баллы:* {user['eco_score']}\n"

        rating_text += f"*Твой уровень:* {user['level']}\n\n"
        rating_text += "Зарабатывай баллы:\n• Смотри советы (+5)\n• Указывай город (+10)\n• Ищи пункты приема (+20)\n• Оставляй отзывы (+15)"

        self.send_message(user_id, rating_text)
        return {'success': True, 'action': 'rating_view'}

    def _handle_feedback(self, user_id, message):
        """Обработка отзывов"""
        feedback_text = message.replace('отзыв', '', 1).replace('feedback', '', 1).strip()

        if not feedback_text:
            feedback_text = "💬 *Чтобы оставить отзыв:*\n\n"
            feedback_text += "1. Напиши `отзыв` и через пробел свой текст\n"
            feedback_text += "2. Например: `отзыв Отличный бот, помог найти пункт приёма!`\n\n"
            feedback_text += "Твой отзыв поможет нам стать лучше! 💚"

            self.send_message(user_id, feedback_text)
            return {'success': True, 'action': 'feedback_info'}

        self.db.add_feedback(user_id, feedback_text)
        self.db.add_user_action(user_id, 'leave_feedback', 15, "Оставил отзыв")

        response_text = (
            f"✅ *Спасибо за отзыв!* +15 баллов! 🌟\n\n"
            f"Мы учтём твоё мнение:\n"
            f"`{feedback_text[:100]}{'...' if len(feedback_text) > 100 else ''}`\n\n"
            f"Твой вклад в развитие эко-сообщества очень важен! 💚"
        )

        self.send_message(user_id, response_text)
        return {'success': True, 'action': 'feedback_submitted'}

    def _handle_city(self, user_id, message):
        """Обработка установки города"""
        city_name = message.replace('город', '', 1).strip()

        if not city_name:
            self.send_message(
                user_id,
                "📍 *Укажи название города:*\n\n"
                "Напиши: `город Москва`\n"
                "или `город Санкт-Петербург`\n\n"
                "Это поможет искать реальные пункты приема!"
            )
            return {'success': False, 'action': 'city_empty'}

        if self.db.update_user_city(user_id, city_name):
            response_text = (
                f"✅ *Город установлен:* {city_name}\n"
                f"+10 баллов к рейтингу! 🌟\n\n"
                f"Теперь я могу:\n"
                f"• Искать реальные пункты приёма на карте\n"
                f"• Показывать ближайшие эко-объекты\n"
                f"• Давать актуальные рекомендации\n\n"
                f"Попробуй команду `пункты` для поиска! 🗺️"
            )

            self.send_message(user_id, response_text)
            return {'success': True, 'action': 'city_set'}
        else:
            self.send_message(user_id, "❌ Ошибка установки города. Попробуй еще раз.")
            return {'success': False, 'action': 'city_set_error'}

    def _handle_settings(self, user_id):
        """Настройки бота"""
        settings_text = (
            f"⚙️ *Настройки бота:*\n\n"
            f"*Доступные опции:*\n"
            f"• Изменить город\n"
            f"• Настроить уведомления\n"
            f"• Выбрать интересы\n"
            f"• О боте и версия\n\n"
            f"Используй меню ниже или команды:\n"
            f"`город [название]` - изменить город\n"
            f"`о боте` - информация о боте"
        )

        self.send_message(user_id, settings_text, Keyboards.get_settings_keyboard())
        return {'success': True, 'action': 'settings'}

    def _handle_thanks(self, user_id):
        """Обработка благодарности"""
        thanks_text = (
            "🙏 *Спасибо тебе!*\n\n"
            "Твоя экологическая осознанность вдохновляет!\n"
            "Каждое маленькое действие имеет значение.\n\n"
            "Продолжай в том же духе! 💚🌍"
        )

        self.send_message(user_id, thanks_text)
        return {'success': True, 'action': 'thanks'}

    def _handle_about(self, user_id):
        """Информация о боте"""
        about_text = (
            f"🤖 *{config.BOT_NAME}*\n\n"
            f"*Версия:* {config.BOT_VERSION}\n"
            f"*Режим:* Тестовый с реальными картами\n\n"
            f"*Новые возможности:*\n"
            f"• Реальный поиск пунктов приема через OpenStreetMap\n"
            f"• Геокодирование городов\n"
            f"• Поиск по геолокации\n"
            f"• Поиск по адресу\n"
            f"• Подробная информация об объектах\n\n"
            f"*Технологии:*\n"
            f"• Python + VK API\n"
            f"• OpenStreetMap API для данных\n"
            f"• Nominatim для геокодирования\n"
            f"• Хранение данных в памяти\n\n"
            f"Спасибо, что помогаешь делать мир чище! 💚"
        )

        self.send_message(user_id, about_text)
        return {'success': True, 'action': 'about'}

    def _handle_map_info(self, user_id):
        """Информация о картографическом сервисе"""
        map_text = (
            "🗺️ *Картографический сервис бота*\n\n"
            "*Источник данных:* OpenStreetMap\n"
            "*Типы объектов:*\n"
            "• Пункты приема вторсырья ♻️\n"
            "• Эко-магазины 🏪\n"
            "• Точки сбора батареек 🔋\n"
            "• Контейнеры для раздельного сбора 🗑️\n\n"
            "*Как использовать:*\n"
            "1. Укажи город: `город Москва`\n"
            "2. Найди пункты: `пункты` или `рядом`\n"
            "3. Получи список с адресами и расстоянием\n\n"
            "*Важно:* Данные обновляются сообществом OSM,\n"
            "поэтому актуальность может варьироваться."
        )

        self.send_message(user_id, map_text)
        return {'success': True, 'action': 'map_info'}

    def _handle_unknown(self, user_id, message):
        """Обработка неизвестной команды"""
        unknown_text = (
            f"🤔 *Не понял команду:* `{message[:50]}{'...' if len(message) > 50 else ''}`\n\n"
            f"*Доступные команды:*\n"
            f"• `помощь` - все команды\n"
            f"• `профиль` - твоя статистика\n"
            f"• `город Москва` - указать город для поиска\n"
            f"• `пункты` - найти реальные пункты приема\n"
            f"• `совет` - эко-совет дня\n"
            f"• `отзыв текст` - оставить отзыв\n\n"
            f"Или используй кнопки меню ниже! 👇"
        )

        self.send_message(user_id, unknown_text)
        return {'success': False, 'action': 'unknown_command'}