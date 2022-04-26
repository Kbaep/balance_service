import requests

def check_value_positive(value) -> bool:

    ''' Проверка рациональности числа'''

    if value > 0:
        return True
    else:
        return False

def currency_value_balance(balance, currency):

    ''' Перевод баланса в другую валюту '''

    info = requests.get(f'https://www.cbr-xml-daily.ru/daily_json.js')
    info = info.json()
    currency_value = info['Valute'][currency]['Value']
    cur_balance = balance/currency_value
    return cur_balance