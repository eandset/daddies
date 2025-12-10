import aiohttp
from typing import List, Dict, Optional


class OverpassIntegration:
    """Минимальная интеграция с Overpass API для поиска эко-точек"""

    def __init__(self):
        self.base_url = "https://overpass-api.de/api/interpreter"
        self.session = None

    async def _get_session(self):
        """Получить или создать HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Закрыть сессию"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def find_eco_points(self, lat: float, lon: float, radius: int = 5000) -> Dict[str, List[Dict]]:
        """
        эко-точки в радиусе указанных координат

        Args:
            lat: Широта
            lon: Долгота
            radius: Радиус поиска в метрах (по умолчанию 5км)

        Returns:
            Словарь с точками по категориям
        """
        # Overpass QL запрос для поиска эко-точек
        query = f"""
        [out:json];
        (
          // Пункты приема отходов
          node["amenity"="recycling"](around:{radius},{lat},{lon});
          node["recycling_type"](around:{radius},{lat},{lon});

          // Парки и зеленые зоны (для мероприятий)
          node["leisure"="park"](around:{radius},{lat},{lon});
          way["leisure"="park"](around:{radius},{lat},{lon});
          relation["leisure"="park"](around:{radius},{lat},{lon});

          // Органические магазины
          node["shop"="organic"](around:{radius},{lat},{lon});
          node["shop"="health_food"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """

        try:
            session = await self._get_session()
            async with session.post(
                    self.base_url,
                    data={'data': query},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    print(f"Overpass API error: {response.status}")
                    return self._get_fallback_points()
        except Exception as e:
            print(f"Error fetching from Overpass: {e}")
            return self._get_fallback_points()

    def _parse_response(self, data: Dict) -> Dict[str, List[Dict]]:
        """Парсим ответ от Overpass API"""
        points = {
            'recycling': [],
            'event': [],
            'eco_shop': []
        }

        if 'elements' not in data:
            return points

        for element in data['elements']:
            point_data = self._extract_point_data(element)
            if point_data:
                category = self._categorize_point(point_data['tags'])
                if category in points:
                    points[category].append(point_data)

        return points

    def _extract_point_data(self, element: Dict) -> Optional[Dict]:
        """Извлекаем данные точки из элемента Overpass"""
        if element['type'] == 'node':
            return {
                'id': element.get('id'),
                'lat': element.get('lat'),
                'lon': element.get('lon'),
                'name': element.get('tags', {}).get('name', 'Неизвестно'),
                'tags': element.get('tags', {}),
                'description': self._generate_description(element.get('tags', {}))
            }
        return None

    def _generate_description(self, tags: Dict) -> str:
        """Генерируем описание точки на основе тегов"""
        descriptions = []

        if 'amenity' in tags and tags['amenity'] == 'recycling':
            descriptions.append("Пункт приема отходов")

        # Добавляем информацию о принимаемых материалах
        recycling_materials = []
        for key, value in tags.items():
            if key.startswith('recycling:') and value == 'yes':
                material = key.replace('recycling:', '')
                recycling_materials.append(material)

        if recycling_materials:
            descriptions.append(f"Принимает: {', '.join(recycling_materials)}")

        if 'opening_hours' in tags:
            descriptions.append(f"Часы работы: {tags['opening_hours']}")

        return ". ".join(descriptions) if descriptions else "Эко-точка"

    def _categorize_point(self, tags: Dict) -> str:
        """Определяем категорию точки"""
        if 'amenity' in tags and tags['amenity'] == 'recycling':
            return 'recycling'
        elif 'leisure' in tags and tags['leisure'] == 'park':
            return 'event'
        elif 'shop' in tags and tags['shop'] in ['organic', 'health_food']:
            return 'eco_shop'
        return 'other'

    def _get_fallback_points(self) -> Dict[str, List[Dict]]:
        """Возвращаем тестовые точки если API недоступно"""
        return {
            'recycling': [
                {
                    'name': 'Эко-Сбор Центр',
                    'description': 'Прием пластика, стекла и бумаги. Работает с 9:00 до 19:00',
                    'lat': None,
                    'lon': None
                }
            ],
            'event': [
                {
                    'name': 'Зеленый Парк',
                    'description': 'Место для субботников и экологических мероприятий',
                    'lat': None,
                    'lon': None
                }
            ],
            'eco_shop': []
        }
