import requests
from bs4 import BeautifulSoup


def scrape_expomap_page(url):
    """
    Функция для получения всех элементов cli-info со страницы expomap.ru
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Загружаем страницу
        print(f"Загружаем страницу: {url}")
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()

        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все div с классом cli-info
        cli_info_elements = soup.find_all('div', class_='cli-info')

        print(f"Найдено {len(cli_info_elements)} элементов cli-info")

        # Собираем данные в список словарей
        events_data = []

        for index, cli_info in enumerate(cli_info_elements, 1):
            event_data = {
                'id': index,
                'html': str(cli_info),  # Полный HTML элемента
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

            # 5. Кнопки
            buttons_div = cli_info.find('div', class_='cli-m-buttons')
            if buttons_div:
                buttons = buttons_div.find_all('a')
                event_data['data']['buttons'] = []
                for btn in buttons:
                    btn_data = {
                        'text': btn.get_text(strip=True),
                        'href': btn.get('href', ''),
                        'class': btn.get('class', [])
                    }
                    event_data['data']['buttons'].append(btn_data)

            # 6. Теги
            tags_div = cli_info.find('div', class_='cli-tags')
            if tags_div:
                tags = tags_div.find_all('a')
                event_data['data']['tags'] = [tag.get_text(strip=True) for tag in tags]
                event_data['data']['tag_links'] = [tag.get('href', '') for tag in tags]

            # 7. Статистика (если есть)
            stats_div = cli_info.find('aside', class_='right_grey_block')
            if stats_div:
                event_data['data']['statistics'] = stats_div.get_text(strip=True)

            events_data.append(event_data)

        return events_data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return None


def main():
    # URL страницы
    url = "https://expomap.ru/expo/theme/ekologiya-ochistka-utilizatsiya/country/russia/"

    # Получаем данные
    events = scrape_expomap_page(url)

    if events:
        print(f"\nУспешно получено {len(events)} событий")

        # Выводим краткую информацию в консоль
        print("\nКраткая информация о событиях:")
        for event in events[:3]:  # Показываем первые 3 события
            data = event['data']
            print(f"\n{event['id']}. {data.get('title', 'Нет заголовка')}")
            print(f"   Дата: {data.get('date', 'Не указана')}")
            print(f"   Место: {data.get('place', 'Не указано')}")
            print(f"   Тегов: {len(data.get('tags', []))}")

        if len(events) > 3:
            print(f"\n... и еще {len(events) - 3} событий")


if __name__ == "__main__":
    main()