import requests
from bs4 import BeautifulSoup
from NormalizeText import *

def scrape_expomap_page(url):
    """
    Функция для получения всех элементов cli-info со страницы expomap.ru
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux Arch; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Загружаем страницу
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        cli_info_elements = soup.find_all('div', class_='cli-info')

        print(f"Найдено {len(cli_info_elements)} элементов cli-info")

        events_data = []

        for index, cli_info in enumerate(cli_info_elements, 1):
            event_data = {
                'id': index,
                'data': {}  # Структурированные данные
            }

            # Извлекаем структурированные данные
            # 1. Заголовок
            header = cli_info.find('header', class_='header-cli-title-pc')
            if header:
                title_div = header.find('div', class_='cli-title')
                if title_div:
                    title_link = title_div.find('a')
                    if title_link:
                        event_data['data']['title'] = title_link.get_text(strip=True)
                        event_data['data']['title_link'] = title_link.get('href', '')

            # 2. Описание
            descr = cli_info.find('div', class_='cli-descr')
            if descr:
                event_data['data']['description'] = descr.get_text(strip=True)

            # 3. Дата
            date_div = cli_info.find('div', class_='cli-date')
            if date_div:
                event_data['data']['date'] = date_div.get_text(strip=True)

            # 4. Место
            place_div = cli_info.find('div', class_='cli-place')
            if place_div:
                event_data['data']['place'] = place_div.get_text(strip=True)

                # Извлекаем отдельные части места
                links = place_div.find_all('a')
                if len(links) >= 2:
                    event_data['data']['country'] = links[0].get_text(strip=True)
                    event_data['data']['city'] = links[1].get_text(strip=True)
                    if len(links) >= 3:
                        event_data['data']['venue'] = links[2].get_text(strip=True)

            # 5. Статистика (если есть)
            stats_div = cli_info.find('aside', class_='right_grey_block')
            if stats_div:
                event_data['data']['statistics'] = str.removeprefix(stats_div.get_text(strip=True), "Масштаб выставки:")

            # 6. Подробнее
            sites = cli_info.find("a", class_="button icon-sm")
            if sites:
                event_data['data']['site'] = sites.get("href")

            events_data.append(event_data)

        return events_data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return None


def get_events():
    # URL страницы
    url = "https://expomap.ru/expo/theme/ekologiya-ochistka-utilizatsiya/country/russia/"

    # Получаем данные
    events = scrape_expomap_page(url)

    if events:
        result = ""
        
        print(f"\nУспешно получено {len(events)} событий")

        print("\nИнформация о событиях:")
        for event in events:
            data = event['data']
            
            result += f"\n{'='*60}\n"
            result += f"🎪 СОБЫТИЕ #{event['id']}\n"
            result += f"{'='*60}\n"

            result += f"📌 Название: {data.get('title', '❌ Не указано')}\n"
            result += f"📝 Описание: {str.strip(data.get('description', '❌ Не указано'))}\n"
            result += f"📊 Статистика: {format_stats(data.get('statistics', '❌ Не указано'))}\n"
            result += f"📅 Дата проведения: {parse_date_string(data.get('date', '❌ Не указано'))}\n"
            result += f"📍 Место: {data.get('place', '❌ Не указано')}\n"
            result += f"🔗 Подробнее: https://expomap.ru{data.get('site', '❌ Нет ссылки')}\n"

            result += f"{'='*60}\n\n"

        return result
    
    return "ошибка получения - нет эвентов" 


if __name__ == "__main__":
    print(get_events())