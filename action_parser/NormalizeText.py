import re

def parse_date_string(date_html):
    """
    Преобразует HTML строку с датой в нормальный формат
    Пример: с 27 по 30 января
    """
    # Убираем HTML теги и лишние пробелы
    text = re.sub(r'<[^>]+>', ' ', date_html)
    text = ' '.join(text.split())  # Нормализуем пробелы

    # Ищем шаблон "с X по Y месяца"
    pattern = r'с\s+(\d+)\s+по\s+(\d+)\s+([а-яА-ЯёЁ]+)'
    match = re.search(pattern, text)

    if match:
        start_day, end_day, month = match.groups()
        return f"{start_day}-{end_day} {month}"

    return text

def format_stats(s: str) -> list:
    # ставим пробел после ':' если за ним сразу цифра
    s = re.sub(r':(?=\d)', ': ', s)
    # вставляем перевод строки между цифрой и следующей буквой
    s = re.sub(r'(?<=\d)(?=[^\W\d_])', '\n', s)
    return s.split("\n")