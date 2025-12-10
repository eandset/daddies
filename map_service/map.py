import requests
from geopy.distance import geodesic
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import re

from position_getter import get_simple_address
from build_path import build_path_and_get_link


class EcoPointType(Enum):
    """Типы экологических точек"""
    RECYCLING = "recycling"  # Пункты переработки
    ECO_SHOP = "eco_shop"    # Эко-магазины
    SECONDHAND = "secondhand"  # Секонд-хенды
    ORGANIC = "organic"      # Органические магазины
    OTHER = "other"          # Другие типы


@dataclass
class EcoPoint:
    """Класс для представления экологической точки"""
    id: int
    osm_type: str  # 'node', 'way', 'relation'
    latitude: float
    longitude: float
    name: str
    point_type: EcoPointType
    tags: Dict[str, Any] = field(default_factory=dict)
    distance_meters: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует точку в словарь для удобства использования"""
        return {
            "id": self.id,
            "type": self.osm_type,
            "lat": self.latitude,
            "lon": self.longitude,
            "name": self._get_display_name(),
            "coordinates": f"{self.latitude:.6f}, {self.longitude:.6f}",
            "kind": self.point_type.value,
            "description": self.get_description(),
            "tags": self.tags,
            "distance": round(self.distance_meters),
            "osm_url": self.get_osm_url()
        }
    
    def _get_display_name(self) -> str:
        """Получает отображаемое имя"""
        if self.name != "—":
            return self.name
        
        # Генерируем имя на основе типа
        if self.point_type == EcoPointType.RECYCLING:
            operator = self.tags.get('operator', '')
            if operator:
                return f"Пункт приёма ({operator})"
            
            recycling_type = self.tags.get('recycling_type', '')
            if recycling_type:
                type_names = {
                    'container': 'Контейнер для раздельного сбора',
                    'centre': 'Центр приёма',
                    'point': 'Пункт приёма',
                    'site': 'Площадка для сбора'
                }
                return type_names.get(recycling_type, 'Пункт переработки')
            
            return "Пункт переработки"
        
        type_names = {
            EcoPointType.ECO_SHOP: "Эко-магазин",
            EcoPointType.SECONDHAND: "Секонд-хенд",
            EcoPointType.ORGANIC: "Органический магазин",
            EcoPointType.OTHER: "Эко-точка"
        }
        return type_names.get(self.point_type, "Эко-точка")
    
    def _clean_material_name(self, material: str) -> str:
        """Очищает название материала"""
        material = re.sub(r';.*$', '', material)
        material = material.replace('_', ' ').strip().lower()
        
        # Преобразуем английские названия в русские
        material_translations = {
            'glass': 'стекло',
            'paper': 'бумага',
            'plastic': 'пластик',
            'scrap metal': 'металл',
            'metal': 'металл',
            'batteries': 'батарейки',
            'clothes': 'одежда',
            'textiles': 'текстиль',
            'electronics': 'электроника',
            'aluminium': 'алюминий',
            'PET': 'ПЭТ',
            'cans': 'банки',
            'plastic bottles': 'пластиковые бутылки',
            'glass bottles': 'стеклянные бутылки',
            'beverage cartons': 'напиточные коробки',
            'tetrapak': 'тетрапак',
            'cardboard': 'картон',
            'newspaper': 'газеты',
            'magazines': 'журналы',
            'books': 'книги',
            'electrical appliances': 'электроприборы',
            'mobile phones': 'мобильные телефоны',
            'computers': 'компьютеры',
            'drugs': 'лекарства',
            'shoes': 'обувь',
            'polystyrene foam': 'пенополистирол',
            'aerosol cans': 'аэрозольные баллончики',
            'plastic bags': 'пластиковые пакеты',
            'blister packaging': 'блистерная упаковка',
            'plastic packaging': 'пластиковая упаковка',
            'paper packaging': 'бумажная упаковка',
            'plasterboard': 'гипсокартон',
            'small appliances': 'мелкая бытовая техника',
            'electrical items': 'электротовары',
            'glass cans': 'стеклянные банки',
            'bottles': 'бутылки',
            'cartons': 'коробки',
            'small electrical appliances': 'мелкая электротехника',
            'waste': 'отходы',
            'refuse': 'мусор',
        }
        
        if material in material_translations:
            return material_translations[material]
        
        # Проверяем частичное совпадение
        for eng, rus in material_translations.items():
            if eng in material:
                return rus
        
        return material.title()
    
    def get_description(self) -> str:
        """Генерирует читаемое описание точки"""
        parts = []
        
        # Тип точки
        if self.point_type == EcoPointType.RECYCLING:
            parts.append("Пункт приёма вторсырья")
        elif self.point_type == EcoPointType.ECO_SHOP:
            parts.append("Эко-магазин")
        elif self.point_type == EcoPointType.SECONDHAND:
            parts.append("Секонд-хенд")
        elif self.point_type == EcoPointType.ORGANIC:
            parts.append("Магазин органических продуктов")
        
        # Что принимают
        if self.point_type == EcoPointType.RECYCLING:
            materials = self._get_accepted_materials()
            if materials:
                parts.append(f"Принимает: {materials}")
        
        # Тип переработки
        recycling_type = self.tags.get('recycling_type')
        if recycling_type:
            type_names = {
                'container': 'Контейнер',
                'centre': 'Центр',
                'point': 'Пункт',
                'site': 'Площадка'
            }
            type_name = type_names.get(recycling_type, recycling_type)
            parts.append(f"Тип: {type_name}")
        
        # Контакты
        if 'contact:phone' in self.tags:
            phone = self.tags['contact:phone']
            if phone and len(phone) < 20:
                parts.append(f"📞 {phone}")
        
        if 'contact:website' in self.tags:
            website = self.tags['contact:website']
            if website and website.startswith('http'):
                domain = website.replace('http://', '').replace('https://', '').split('/')[0]
                parts.append(f"🌐 {domain}")
        
        # Оператор
        operator = self.tags.get('operator')
        if operator and len(operator) < 30:
            parts.append(f"Оператор: {operator}")
        
        # Часы работы
        if 'opening_hours' in self.tags:
            hours = self.tags['opening_hours']
            if hours and len(hours) < 50:
                parts.append(f"🕒 {hours}")
        
        return " • ".join(parts) if parts else "Информация отсутствует"
    
    def _get_accepted_materials(self) -> str:
        """Получает список принимаемых материалов"""
        recycling_keys = [k for k in self.tags.keys() if k.startswith('recycling:')]
        materials = []
        
        for key in recycling_keys:
            if key.startswith('recycling:'):
                material = key.split(':')[1]
                if self.tags[key] == 'yes':
                    clean_material = self._clean_material_name(material)
                    materials.append(clean_material)
        
        # Убираем дубликаты
        materials = list(dict.fromkeys(materials))
        
        if not materials:
            return ""
        
        # Ограничиваем для читаемости
        if len(materials) > 5:
            main_materials = materials[:4]
            return f"{', '.join(main_materials)} и другие"
        
        return ', '.join(materials)
    
    def get_osm_url(self) -> str:
        """Возвращает ссылку на объект в OpenStreetMap"""
        return f"https://www.openstreetmap.org/{self.osm_type}/{self.id}"
    
    def __str__(self) -> str:
        """Строковое представление точки"""
        return f"{self._get_display_name()}"


class EcoPointFinder:
    """Класс для поиска и обработки экологических точек"""
    
    OVER_PASS_URL = "https://overpass-api.de/api/interpreter"
    
    @classmethod
    def _osm_to_eco_point(cls, element: Dict[str, Any]) -> Optional[EcoPoint]:
        """Преобразует элемент OSM в объект EcoPoint"""
        try:
            # Получаем координаты
            lat = None
            lon = None
            
            if element['type'] == 'node':
                lat = element.get('lat')
                lon = element.get('lon')
            else:  # way/relation
                center = element.get('center')
                if center:
                    lat = center.get('lat')
                    lon = center.get('lon')
            
            if lat is None or lon is None:
                return None
            
            # Получаем теги
            tags = element.get('tags', {})
            
            # Определяем название
            name = tags.get('name', '—')
            
            # Определяем тип точки
            point_type = cls._determine_point_type(tags)
            
            # Создаём точку
            eco_point = EcoPoint(
                id=element.get('id'),
                osm_type=element.get('type'),
                latitude=lat,
                longitude=lon,
                name=name,
                point_type=point_type,
                tags=tags
            )
            
            return eco_point
            
        except Exception as e:
            print(f"Ошибка преобразования элемента OSM: {e}")
            return None
    
    @staticmethod
    def _determine_point_type(tags: Dict[str, Any]) -> EcoPointType:
        """Определяет тип точки на основе тегов"""
        amenity = tags.get('amenity')
        shop = tags.get('shop')
        
        if amenity == 'recycling':
            return EcoPointType.RECYCLING
        elif shop == 'eco':
            return EcoPointType.ECO_SHOP
        elif shop == 'secondhand':
            return EcoPointType.SECONDHAND
        elif shop == 'organic':
            return EcoPointType.ORGANIC
        elif 'recycling' in tags:
            return EcoPointType.RECYCLING
        else:
            return EcoPointType.OTHER
    
    @classmethod
    def find_points(cls, latitude: float, longitude: float, radius_m: int = 2000) -> List[EcoPoint]:
        """Находит экологические точки в радиусе от заданных координат"""
        query = f"""
        [out:json][timeout:25];
        (
          // Пункты переработки
          node(around:{radius_m},{latitude},{longitude})["amenity"="recycling"];
          way(around:{radius_m},{latitude},{longitude})["amenity"="recycling"];
          relation(around:{radius_m},{latitude},{longitude})["amenity"="recycling"];
          
          // Эко-магазины
          node(around:{radius_m},{latitude},{longitude})["shop"="eco"];
          way(around:{radius_m},{latitude},{longitude})["shop"="eco"];
          
          // Секонд-хенды
          node(around:{radius_m},{latitude},{longitude})["shop"="secondhand"];
          
          // Органические магазины
          node(around:{radius_m},{latitude},{longitude})["shop"="organic"];
        );
        out center;
        """
        
        try:
            response = requests.post(cls.OVER_PASS_URL, data={'data': query})
            response.raise_for_status()
            data = response.json()
            
            # Преобразуем элементы OSM в объекты EcoPoint
            eco_points = []
            for element in data.get('elements', []):
                eco_point = cls._osm_to_eco_point(element)
                if eco_point:
                    eco_points.append(eco_point)
            
            return eco_points
            
        except requests.RequestException as e:
            print(f"Ошибка запроса к Overpass API: {e}")
            return []
        except Exception as e:
            print(f"Ошибка обработки данных: {e}")
            return []
    
    @staticmethod
    def calculate_distances(points: List[EcoPoint], user_lat: float, user_lon: float) -> List[EcoPoint]:
        """Рассчитывает расстояния от пользователя до каждой точки"""
        user_location = (user_lat, user_lon)
        
        for point in points:
            point_location = (point.latitude, point.longitude)
            point.distance_meters = geodesic(user_location, point_location).meters
        
        return points
    
    @staticmethod
    def get_nearest_points(points: List[EcoPoint], limit: int = 10) -> List[EcoPoint]:
        """Возвращает ближайшие точки, отсортированные по расстоянию"""
        return sorted(points, key=lambda p: p.distance_meters)[:limit]
    
    @staticmethod
    def filter_by_type(points: List[EcoPoint], point_type: EcoPointType) -> List[EcoPoint]:
        """Фильтрует точки по типу"""
        return [p for p in points if p.point_type == point_type]
    
    @classmethod
    def get_points_for_bot(cls, latitude: float, longitude: float, radius_m: int = 2000, limit: int = 8) -> List[Dict]:
        """Метод для удобного получения точек в формате для бота"""
        points = cls.find_points(latitude, longitude, radius_m)
        points = cls.calculate_distances(points, latitude, longitude)
        nearest = cls.get_nearest_points(points, limit)
        
        return [point.to_dict() for point in nearest]

def get_cool_coords(user_lat, user_lon, radius_m=2000, limit=5):
    points_for_bot = EcoPointFinder.get_points_for_bot(user_lat, user_lon, radius_m, limit)
    
    if not points_for_bot:
        return "❌ Точек не найдено"
    else:
        result = ""

        # Вывод для бота
        for i, point in enumerate(points_for_bot, 1):
            result += f"{i}. 🏢 {point['name']}\n"
            result += f"  📝 {point['description']}\n"

            coord = point['coordinates']
            loc = str.split(coord, ', ')
            lat = loc[0]
            lon = loc[1]

            result += f"{get_simple_address(lat, lon)}"
            result += f"    📏 Расстояние: {point['distance']} м\n"
            result += f"    🗺️ Маршрут: {build_path_and_get_link(f"{user_lat}, {user_lon}", coord)}\n\n"

        return result

# Демонстрация работы
if __name__ == "__main__":
    # Координаты пользователя
    user_lat, user_lon = 55.7558, 37.6176
    
    print("🔍 Поиск эко-точек...")
    print(f"📍 Координаты: {user_lat}, {user_lon}")
    print("=" * 60)
    
    # Получаем точки
    result = get_cool_coords(user_lat, user_lon)

    print(result)