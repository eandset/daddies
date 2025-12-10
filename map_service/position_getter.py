from geopy.geocoders import Nominatim

dictKeys = {
    "road": "Улица",
    "quarter": "Дом",
    "neighbourhood": "Район",
    "suburb": "Подрайон",
    "postcode": "Почтовый код",
    "city": "Город",
}
dictKeys = {
    "road": "🚗 Улица",
    "quarter": "🏠 Дом / Квартал",
    "neighbourhood": "🏘️ Район",
    "suburb": "🏡 Подрайон / Пригород",
    "postcode": "📮 Почтовый код",
    "city": "🏙️ Город",
    "town": "🏙️ Городок",
    "house_number": "🏠 Номер дома",
    "state": "🗺️ Регион / Область",
    "village": "🌳 Село / Деревня",
    "building": "🏢 Здание",
    "amenity": "🏪 Объект инфраструктуры",
    "tourism": "🏨 Туристический объект",
    "shop": "🛒 Магазин",
    "office": "🏢 Офис",
    "historic": "🏰 Исторический объект",
}

def get_simple_address(lat, lon) -> str: 
    """
    Получает город, улицу и номер дома по координатам
    """
    geolocator = Nominatim(
        user_agent="my_geocoder_app/1.0",
        timeout=10,
        domain="nominatim.openstreetmap.org"
    )
    
    try:
        location = geolocator.reverse(
            f"{lat}, {lon}",
            language='ru',
            addressdetails=True,
            zoom=18
        )
        
        if not location:
            return "Адрес не найден"
        
        address = location.raw.get('address', {})
        
        # Выводим полную информацию о адресе для отладки
        result = ""
        for key, value in address.items():
            if dictKeys.get(key):
                result += f"  {dictKeys[key]}: {value}\n"
        
        return result
        
    except Exception as e:
        return f"Ошибка: {e}"

# Пример использования
# if __name__ == "__main__":
#     # Тестовые координаты из вашего HTML (Москва, Красная площадь)
#     test_coordinates = [
#         (55.755388, 37.623313),  # Координаты из вашего HTML
#         (55.7555, 37.623313),    # Красная площадь
#         (55.751244, 37.618423),  # Москва, Кремль
#     ]
    
#     for lat, lon in test_coordinates:
#         print("=" * 80)
#         print(f"ТЕСТ КООРДИНАТ: {lat}, {lon}")
#         print()
        
#         print("1. Используя geopy:")
#         print(get_simple_address(lat, lon))
#         print()