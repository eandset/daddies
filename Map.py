import requests
from geopy.distance import geodesic
import folium
from folium.plugins import MarkerCluster

OVER_PASS_URL = "https://overpass-api.de/api/interpreter"

def over_pass_query(lat, lon, radius_m=2000):
    q = f"""
    [out:json][timeout:25];
    (
      node(around:{radius_m},{lat},{lon})["amenity"="recycling"];
      way(around:{radius_m},{lat},{lon})["amenity"="recycling"];
      relation(around:{radius_m},{lat},{lon})["amenity"="recycling"];
      node(around:{radius_m},{lat},{lon})["shop"="eco"];
      node(around:{radius_m},{lat},{lon})["shop"="organic"];
      node(around:{radius_m},{lat},{lon})["shop"="secondhand"];
      way(around:{radius_m},{lat},{lon})["shop"="eco"];
      relation(around:{radius_m},{lat},{lon})["shop"="eco"];
    );
    out center;
    """
    resp = requests.post(OVER_PASS_URL, data={'data': q})
    resp.raise_for_status()
    return resp.json()

def parse_elements(osm_json):
    points = []
    for el in osm_json.get('elements', []):
        lat = None
        lon = None
        if el['type'] == 'node':
            lat = el.get('lat'); lon = el.get('lon')
        else:  # way/relation
            c = el.get('center')
            if c:
                lat = c.get('lat'); lon = c.get('lon')
        if lat is None or lon is None:
            continue
        tags = el.get('tags', {})
        name = tags.get('name', '—')
        kind = tags.get('amenity') or tags.get('shop') or tags.get('recycling') or 'unknown'
        points.append({
            'id': el.get('id'),
            'type': el.get('type'),
            'lat': lat, 'lon': lon,
            'name': name,
            'kind': kind,
            'tags': tags
        })
    return points

def get_nea_rest(points, user_location, topn=10):
    for p in points:
        p['distm'] = geodesic(user_location, (p['lat'], p['lon'])).meters
    points.sort(key=lambda x: x['distm'])
    return points[:topn]

def build_map(user_location, points):
    m = folium.Map(location=user_location, zoomstart=14, tiles='OpenStreetMap')
    folium.Marker(location=user_location, popup='Вы здесь', icon=folium.Icon(color='blue', icon='user')).add_to(m)
    mc = MarkerCluster().add_to(m)
    for p in points:
        popup = f"{p['name']} ({p['kind']})<br>{p['distm']:.0f} м<br><a href='https://www.openstreetmap.org/{p['type']}/{p['id']}' target='_blank'>OSM</a>"
        folium.Marker(location=(p['lat'], p['lon']), popup=popup, icon=folium.Icon(color='green' if 'shop' in p['kind'] or 'eco' in p['kind'] else 'darkgreen')).add_to(mc)
    return m

# Пример использования:
user_lat, user_lon = 55.7558, 37.6176  # Москва, пример
osm = over_pass_query(user_lat, user_lon, 3000)
pts = parse_elements(osm)
nearest = get_nea_rest(pts, (user_lat, user_lon), topn=20)
map_object = build_map((user_lat, user_lon), nearest)
map_object.save('recyclemap.html')