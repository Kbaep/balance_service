from app import client, Base, engine
import json

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def test_get_no_user():
    # Проверка, отсутствие пользователя в БД
    response = client.get('/balance/?user_id=test_1')
    assert response.status_code == 400
    # body = json.loads(response.data)
    # assert body == {'message': 'Пользователь не существует'}


def test_get_balance_user():
    # Создание пользователя
    body = {
        "method": "add",
        "number": 1000,
        "comment": "Пополнение"
    }
    response = client.post('/balance/test_1', json=body)
    assert response.status_code == 201

    # Проверка баланса пользователя без валюты
    response = client.get('/balance/?user_id=test_1')
    assert response.status_code == 200

    # Не указан пользователь
    response = client.get('/balance/')
    assert response.status_code == 400

    # Проверка баланса с другой валютой
    response = client.get('/balance/?currency=USD&user_id=test_1')
    assert response.status_code == 200

    # Указана не корректная валюта
    response = client.get('/balance/?currency=US&user_id=test_1')
    assert response.status_code == 400


def test_update_balance():
    # Тестирование в изменении баланса пользователя

    # Проверка создания пользователя с передачей минусовой суммы
    body = {
        "method": "add",
        "number": -1000,
        "comment": "Пополнение"
    }
    response = client.post('/balance/test_2', json=body)
    assert response.status_code == 400

    # Создание пользователя
    body = {
        "method": "add",
        "number": 1000,
        "comment": "Пополнение"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 201

    # Пополнения баланса
    body = {
        "method": "add",
        "number": 1000,
        "comment": "Пополнение"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 200

    # Отсутствует комментарий при пополнении
    body = {
        "method": "add",
        "number": 1000
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 400

    # Пополнение с отрицательной суммой
    body = {
        "method": "add",
        "number": -1000,
        "comment": "Пополнение"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 400

    # Покупка, расход баланса
    body = {
        "method": "remove",
        "number": 500,
        "comment": "Покупка утюга"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 200

    # Покупка, расход баланса с отрицательной суммой
    body = {
        "method": "remove",
        "number": -500,
        "comment": "Покупка утюга"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 400

    # Покупка, расход баланса с отрицательной суммой
    body = {
        "method": "remove",
        "number": 9500,
        "comment": "Покупка утюга"
    }
    response = client.post('/balance/test_3', json=body)
    assert response.status_code == 400


def test_transfer():
    # Перевод отрицательную сумму пользователю
    body = {
        "user_id_from": "test_3",
        "user_id_to": "test_1",
        "number": -1000,
        "comment": "Перевод"
    }
    response = client.post('/transfer', json=body)
    assert response.status_code == 400

    # Перевод средств пользователю
    body = {
        "user_id_from": "test_3",
        "user_id_to": "test_1",
        "number": 1000,
        "comment": "Перевод"
    }
    response = client.post('/transfer', json=body)
    assert response.status_code == 200
    # Перевод средств, от несуществующего пользователя
    body = {
        "user_id_from": "test_unknown",
        "user_id_to": "test_1",
        "number": 1000,
        "comment": "Перевод"
    }
    response = client.post('/transfer', json=body)
    assert response.status_code == 400

    # Перевод средств, несуществующему пользователю
    body = {
        "user_id_from": "test_3",
        "user_id_to": "test_unknown",
        "number": 1000,
        "comment": "Перевод"
    }
    response = client.post('/transfer', json=body)
    assert response.status_code == 400

    # Перевод средств, превышающий баланс отправителя
    body = {
        "user_id_from": "test_3",
        "user_id_to": "test_1",
        "number": 100000,
        "comment": "Перевод"
    }
    response = client.post('/transfer', json=body)
    assert response.status_code == 400
#
def test_history_transactions():
    # Запрос истории транзакций по времени по убыванию
    response = client.get('/transactions/?user_id=test_3&sort=create_time&reverse=true')
    assert response.status_code == 200
    # Запрос истории транзакций по времени по увеличению
    response = client.get('/transactions/?user_id=test_3&sort=create_time')
    assert response.status_code == 200
    # Запрос истории транзакций по сумме по убыванию
    response = client.get('/transactions/?user_id=test_3&sort=amount&reverse=true')
    assert response.status_code == 200
    # Запрос истории транзакций по сумме по увеличению
    response = client.get('/transactions/?user_id=test_3')
    assert response.status_code == 200
    # Пользователь не существует
    response = client.get('/transactions/?user_id=test_unknown')
    assert response.status_code == 400