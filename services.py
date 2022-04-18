def check_value_positive(value) -> bool:

    ''' Проверка рациональности числа'''

    if value > 0:
        return True
    else:
        return False
def currency_value_balance(balance, currency):
    if currency == 'USD':
        balance = balance/76
        return balance