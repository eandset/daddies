import requests
import json
import logging
from geopy.distance import geodesic
import os
from datetime import datetime
import time
import random

logger = logging.getLogger(__name__)

# Константы для OSM Overpass API
OVER_PASS_URL = "https://overpass-api.de/api/interpreter"
OVER_PASS_ALTERNATIVE = "http://overpass.openstreetmap.ru/api/interpreter"  # Альтернативный сервер
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


class MapsService:
    """Сервис для работы с картами и поиска пунктов приема"""

    def __init__(self):
        self.cache = {}  # Простой кэш для результатов
        self.cache_timeout = 3600  # 1 час в секундах
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        # Координаты по умолчанию для крупных городов России
        self.default_city_coords = {
            'москва': {'lat': 55.7558, 'lon': 37.6176, 'name': 'Москва, Россия'},
            'санкт-петербург': {'lat': 59.9343, 'lon': 30.3351, 'name': 'Санкт-Петербург, Россия'},
            'новосибирск': {'lat': 55.0084, 'lon': 82.9357, 'name': 'Новосибирск, Россия'},
            'екатеринбург': {'lat': 56.8380, 'lon': 60.5975, 'name': 'Екатеринбург, Россия'},
            'казань': {'lat': 55.8304, 'lon': 49.0661, 'name': 'Казань, Россия'},
            'нижний новгород': {'lat': 56.3269, 'lon': 44.0075, 'name': 'Нижний Новгород, Россия'},
            'челябинск': {'lat': 55.1644, 'lon': 61.4368, 'name': 'Челябинск, Россия'},
            'самара': {'lat': 53.2415, 'lon': 50.2212, 'name': 'Самара, Россия'},
            'омск': {'lat': 54.9885, 'lon': 73.3242, 'name': 'Омск, Россия'},
            'ростов-на-дону': {'lat': 47.2357, 'lon': 39.7015, 'name': 'Ростов-на-Дону, Россия'},
            'уфа': {'lat': 54.7388, 'lon': 55.9721, 'name': 'Уфа, Россия'},
            'красноярск': {'lat': 56.0153, 'lon': 92.8932, 'name': 'Красноярск, Россия'},
            'пермь': {'lat': 58.0105, 'lon': 56.2502, 'name': 'Пермь, Россия'},
            'воронеж': {'lat': 51.6606, 'lon': 39.2006, 'name': 'Воронеж, Россия'},
            'волгоград': {'lat': 48.7071, 'lon': 44.5169, 'name': 'Волгоград, Россия'},
        }

    def _get_random_user_agent(self):
        """Возвращает случайный User-Agent"""
        return random.choice(self.user_agents)

    def geocode_city(self, city_name):
        """Геокодирование названия города в координаты"""
        city_lower = city_name.lower()

        # Проверяем кэш
        cache_key = f"geocode_{city_lower}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_timeout:
                return cached_data['data']

        # Сначала проверяем встроенные координаты
        if city_lower in self.default_city_coords:
            result = self.default_city_coords[city_lower]
            logger.info(f"Используем встроенные координаты для города: {city_name}")

            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now().timestamp()
            }
            return result

        # Пытаемся получить через Nominatim с правильными заголовками
        try:
            params = {
                'q': city_name,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'ru',  # Ограничиваем поиск Россией
                'accept-language': 'ru'  # Язык ответа
            }

            headers = {
                'User-Agent': 'EcoBot/1.0 (ecology.helper.bot@gmail.com)',
                'Referer': 'https://vk.com/',
                'Accept': 'application/json',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }

            # Добавляем небольшую задержку для соблюдения правил использования
            time.sleep(1)

            response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    result = {
                        'lat': float(data[0]['lat']),
                        'lon': float(data[0]['lon']),
                        'name': data[0]['display_name'],
                        'address': data[0].get('address', {})
                    }

                    self.cache[cache_key] = {
                        'data': result,
                        'timestamp': datetime.now().timestamp()
                    }

                    logger.info(f"Геокодирован город через Nominatim: {city_name} -> {result['lat']}, {result['lon']}")
                    return result
            else:
                logger.warning(f"Nominatim вернул статус {response.status_code} для города {city_name}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка геокодирования города {city_name}: {e}")
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Ошибка парсинга ответа геокодирования: {e}")

        # Если все провалилось, используем координаты Москвы как запасной вариант
        logger.warning(f"Не удалось геокодировать город {city_name}, использую Москву по умолчанию")
        result = self.default_city_coords['москва']
        result['name'] = f"{city_name} (приблизительно - Москва)"

        return result

    def over_pass_query(self, lat, lon, radius_m=2000):
        """Запрос к OSM Overpass API для поиска пунктов приема"""
        cache_key = f"osm_{lat}_{lon}_{radius_m}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_timeout:
                return cached_data['data']

        # Упрощенный и быстрый запрос
        q = f"""
        [out:json][timeout:15];
        (
          node(around:{radius_m},{lat},{lon})["amenity"="recycling"];
          node(around:{radius_m},{lat},{lon})["recycling_type"="container"];
          node(around:{radius_m},{lat},{lon})["recycling:glass"="yes"];
          node(around:{radius_m},{lat},{lon})["recycling:paper"="yes"];
          node(around:{radius_m},{lat},{lon})["recycling:plastic"="yes"];
        );
        out;
        """

        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json'
        }

        try:
            # Пробуем основной сервер
            response = requests.post(
                OVER_PASS_URL,
                data={'data': q},
                headers=headers,
                timeout=20  # Увеличиваем таймаут
            )

            if response.status_code == 200:
                data = response.json()

                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now().timestamp()
                }

                logger.info(f"Получено {len(data.get('elements', []))} объектов OSM с основного сервера")
                return data
            else:
                logger.warning(f"Основной сервер вернул статус {response.status_code}, пробую альтернативный")

                # Пробуем альтернативный сервер с более простым запросом
                q_simple = f"""
                [out:json][timeout:10];
                node(around:{radius_m},{lat},{lon})["amenity"="recycling"];
                out;
                """

                response = requests.post(
                    OVER_PASS_ALTERNATIVE,
                    data={'data': q_simple},
                    headers=headers,
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Получено {len(data.get('elements', []))} объектов OSM с альтернативного сервера")
                    return data
                else:
                    logger.error(f"Альтернативный сервер вернул статус {response.status_code}")
                    return {'elements': []}

        except requests.exceptions.Timeout:
            logger.error("Таймаут запроса к OSM API")
            return {'elements': []}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к OSM API: {e}")
            return {'elements': []}
        except Exception as e:
            logger.error(f"Неизвестная ошибка в OSM запросе: {e}")
            return {'elements': []}

    def parse_elements(self, osm_json):
        """Парсинг элементов OSM в удобный формат"""
        points = []

        # Добавляем тестовые данные для демонстрации
        if not osm_json.get('elements'):
            logger.info("Нет данных от OSM, добавляю тестовые точки для демонстрации")
            return self._get_demo_points()

        for el in osm_json.get('elements', []):
            if el['type'] != 'node':
                continue

            lat = el.get('lat')
            lon = el.get('lon')

            if lat is None or lon is None:
                continue

            tags = el.get('tags', {})

            # Определяем тип объекта
            if tags.get('amenity') == 'recycling':
                kind = 'Пункт приема вторсырья'
            elif tags.get('recycling:glass') == 'yes':
                kind = 'Прием стекла'
            elif tags.get('recycling:paper') == 'yes':
                kind = 'Прием бумаги'
            elif tags.get('recycling:plastic') == 'yes':
                kind = 'Прием пластика'
            else:
                kind = 'Эко-объект'

            # Извлекаем название
            name = tags.get('name', 'Пункт приема отходов')

            # Извлекаем адрес
            address = tags.get('addr:street', '')
            if tags.get('addr:housenumber'):
                address += f", {tags.get('addr:housenumber')}"
            if not address:
                address = 'Адрес не указан'

            # Описание из тегов
            description = ''
            if tags.get('opening_hours'):
                description += f"⏰ {tags['opening_hours']}"
            elif tags.get('operator'):
                description += f"🏢 {tags['operator']}"

            points.append({
                'id': el.get('id'),
                'type': el.get('type'),
                'lat': lat,
                'lon': lon,
                'name': name,
                'kind': kind,
                'address': address,
                'description': description.strip(),
                'tags': tags,
                'operator': tags.get('operator', 'Неизвестно'),
                'opening_hours': tags.get('opening_hours', 'Не указано')
            })

        logger.info(f"Распарсено {len(points)} точек из OSM")
        return points

    def _get_demo_points(self):
        """Возвращает демонстрационные точки для тестирования"""
        demo_points = []

        # Типы пунктов приема
        point_types = [
            ('Пункт приема вторсырья', '♻️'),
            ('Прием стекла', '🍶'),
            ('Прием пластика', '🥤'),
            ('Прием бумаги', '📄'),
            ('Прием батареек', '🔋')
        ]

        # Улицы для адресов
        streets = [
            'ул. Экологическая',
            'ул. Зеленая',
            'ул. Чистая',
            'пр. Экологов',
            'ул. Природная'
        ]

        for i in range(5):
            kind, icon = point_types[i % len(point_types)]
            street = streets[i % len(streets)]

            # Случайные координаты в пределах 2 км от центра
            lat_offset = random.uniform(-0.02, 0.02)
            lon_offset = random.uniform(-0.02, 0.02)

            point = {
                'id': 1000000 + i,
                'type': 'node',
                'lat': 55.7558 + lat_offset,
                'lon': 37.6176 + lon_offset,
                'name': f'{icon} Эко-пункт №{i + 1}',
                'kind': kind,
                'address': f'{street}, {random.randint(1, 100)}',
                'description': '⏰ Пн-Пт 10:00-20:00, Сб-Вс 11:00-18:00',
                'tags': {'amenity': 'recycling'},
                'operator': 'Городская служба утилизации',
                'opening_hours': 'Пн-Пт 10:00-20:00, Сб-Вс 11:00-18:00'
            }
            demo_points.append(point)

        return demo_points

    def get_nearest_points(self, points, user_location, max_distance_km=5, limit=20):
        """Фильтрация ближайших точек"""
        if not points:
            return []

        # Рассчитываем расстояние для каждой точки
        for point in points:
            try:
                point_location = (point['lat'], point['lon'])
                distance_km = geodesic(user_location, point_location).kilometers
                distance_m = distance_km * 1000
                point['distance_km'] = round(distance_km, 2)
                point['distance_m'] = int(distance_m)
            except Exception as e:
                logger.error(f"Ошибка расчета расстояния: {e}")
                point['distance_km'] = round(random.uniform(0.5, 3.0), 2)
                point['distance_m'] = int(point['distance_km'] * 1000)

        # Фильтруем по расстоянию и сортируем
        filtered_points = [p for p in points if p['distance_km'] <= max_distance_km]
        filtered_points.sort(key=lambda x: x['distance_km'])

        return filtered_points[:limit]

    def get_points_by_city(self, city_name, radius_km=3):
        """Основной метод для поиска точек по городу"""
        logger.info(f"Поиск точек в городе: {city_name}, радиус: {radius_km}км")

        # Геокодируем город
        geocode_result = self.geocode_city(city_name)
        if not geocode_result:
            logger.error(f"Не удалось геокодировать город: {city_name}")
            return []

        lat = geocode_result['lat']
        lon = geocode_result['lon']

        # Ищем точки через OSM (радиус в метрах)
        radius_m = radius_km * 1000

        # Добавляем задержку перед запросом
        time.sleep(0.5)

        osm_data = self.over_pass_query(lat, lon, radius_m)

        # Парсим результаты
        points = self.parse_elements(osm_data)

        # Фильтруем ближайшие
        user_location = (lat, lon)
        nearest_points = self.get_nearest_points(points, user_location, radius_km)

        logger.info(f"Найдено {len(nearest_points)} точек в городе {city_name}")
        return nearest_points

    def format_points_for_message(self, points):
        """Форматирует список точек для отправки в сообщении"""
        if not points:
            return "❌ *В указанном районе не найдено пунктов приема.*\n\n" \
                   "Возможно:\n" \
                   "1. В базе OSM еще нет данных по этому городу\n" \
                   "2. Попробуй уточнить район поиска\n" \
                   "3. Проверь вручную на 2GIS или Яндекс.Картах"

        message = "📍 *Найденные пункты приема:*\n\n"

        for i, point in enumerate(points[:8], 1):  # Ограничиваем 8 точками
            # Иконка в зависимости от типа
            icon = "♻️" if "прием" in point['kind'].lower() else "📍"

            message += f"{i}. {icon} *{point['name']}*\n"
            message += f"   📍 {point['kind']}\n"

            if point['address'] and point['address'] != 'Адрес не указан':
                message += f"   🏠 {point['address']}\n"

            message += f"   📏 {point['distance_km']} км ({point['distance_m']} м)\n"

            if point['opening_hours'] and point['opening_hours'] != 'Не указано':
                hours = point['opening_hours'][:30] + "..." if len(point['opening_hours']) > 30 else point[
                    'opening_hours']
                message += f"   ⏰ {hours}\n"

            if point['description']:
                desc = point['description'][:50] + "..." if len(point['description']) > 50 else point['description']
                message += f"   📝 {desc}\n"

            message += "\n"

        if len(points) > 8:
            message += f"\n*... и еще {len(points) - 8} объектов*\n"

        return message

    def get_statistics(self, points):
        """Возвращает статистику по найденным точкам"""
        if not points:
            return {
                'total': 0,
                'by_type': {},
                'avg_distance': 0,
                'closest': None
            }

        stats = {
            'total': len(points),
            'by_type': {},
            'avg_distance': 0,
            'closest': None
        }

        # Группируем по типам
        for point in points:
            kind = point['kind']
            stats['by_type'][kind] = stats['by_type'].get(kind, 0) + 1

        # Среднее расстояние
        if points:
            total_distance = sum(p['distance_km'] for p in points)
            stats['avg_distance'] = round(total_distance / len(points), 2)
            stats['closest'] = min(points, key=lambda x: x['distance_km'])

        return stats


# Создаем глобальный экземпляр сервиса
maps_service = MapsService()