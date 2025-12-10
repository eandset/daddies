
def eco_status(score: int) -> str:
    rank = {
        0: 'Эко-что?',
        10: 'Начинающий',
        50: 'Эко-пионер',
        100: 'Знаток',
        250: 'Активист',
        500: 'Герой',
        1000: 'Гуру'
    }

    result = None
    for num, name in rank.items():
        if score >= num:
            result = name
        else:
            break
    
    return result


