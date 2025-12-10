def build_path_and_get_link(start_coords_str, end_coords_str, zoom=17):
    """
    Создает ссылку на маршрут в OpenStreetMap
    
    Аргументы:
    start_coords_str: str - "широта, долгота" старта
    end_coords_str: str - "широта, долгота" финиша
    engine: str - движок построения маршрута
    zoom: int - уровень масштабирования карты (10-19)
    
    Возвращает:
    str - ссылка на маршрут в OSM
    """
    try:
        start_lat, start_lon = map(float, start_coords_str.strip().split(','))
        end_lat, end_lon = map(float, end_coords_str.strip().split(','))
        
        route_part = f"{start_lat}%2C{start_lon}%3B{end_lat}%2C{end_lon}"
        
        # Рассчитываем центр карты для лучшего отображения
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        
        url = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={route_part}#map={zoom}/{center_lat}/{center_lon}"
        
        return url
        
    except Exception as e:
        return f"Ошибка: {e}"

# Примеры использования
# if __name__ == "__main__":
#     # Тестовые координаты
#     start = "55.756477,37.626991"
#     end = "55.755472,37.624765"
    
#     print("=" * 60)
#     print("ССЫЛКИ НА МАРШРУТЫ В OPENSTREETMAP")
#     print("=" * 60)
    
#     # 1. Основная функция
#     print("\n1. Маршрут на машине:")
#     link1 = build_path_and_get_link(start, end)
#     print(f"   Ссылка: {link1}")