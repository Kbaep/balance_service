# Микросервис для работы с балансом пользователей.

Microservice for working with user balance flask реализован микросервис для работы с балансом пользователей (зачисление
средств, списание средств, перевод средств от пользователя к пользователю, а также метод получения баланса пользователя)
. Сервис предоставляет HTTP API и принимает/отдаёт запросы/ответы в формате JSON.

# Подготовка:

В проекте используется Python v3.8

В файле `requirements.txt`, указан список использующихся библиотек. Его можно установить по команде в консоле: pip
install -r requirements.txt

# Методы:

## Метод current_balance принимает наименование пользователя и возвращает информацию о балансе пользователя и его id.

`GET /balance/`- возвращает информацию о балансе пользователя.

Параметры:

* `user_id` – пользователь
* `currency` – пересчет баланса в другой валюте

### Пример запроса

`GET /balance/?currency=USD&user_id=Stepan`

### Ответ

Успешный ответ приходит с кодом `200 OK` и содержит тело:

```json
{
  "balance": 30.19,
  "currency": "USD",
  "id": 4,
  "user_id": "Stepan"
}
```

### Пример запроса

`GET /balance/?user_id=Stepan`

### Ответ

Успешный ответ приходит с кодом `200 OK` и содержит тело:

```json
{
  "balance": 2000.0,
  "id": 4,
  "user_id": "Stepan"
}
```

## Метод update_balance принимает наименование пользователя и json и производит начисление или списание средств.

`POST /balance/<string:user_id>`

Параметры body json:

* `method` – может принимать `add` и `remove`
* `number` – сумма денег
* `comment` – комментарий к операции, если не указать, тогда по умолчанию "Неизвестно"

### Пример запроса

`Post /balance/Stepan`

json:

```json
{
  "method": "add",
  "number": 1000,
  "comment": "Пополнение"
}
```

### Ответ

Успешный ответ приходит с кодом `201 OK`, если пользователь не существует в БД, или `200 OK` для существующего
пользователя, без содержания тела.

### Пример запроса

`POST /balance/Stepan`

json:

```json
{
  "method": "remove",
  "number": 500,
  "comment": "Покупка утюга"
}
```

### Ответ

Успешный ответ приходит с кодом `200 OK` без содержания тела.

## Метод transfer принимает наименование json и переводит средства от одного пользователя, другому.

`POST /transfer` перевод средств

Параметры:

* `user_id_from` – от кого будет переведено
* `user_id_to` – кому будет передена сумма
* `number` – сумма денег
* `comment` – комментарий к операции, если не указать, тогда по умолчанию "Неизвестно"

### Пример запроса

`POST /transfer`

```json
{
  "user_id_from": "Pavel",
  "user_id_to": "Stepan",
  "number": 1000,
  "comment": "Перевод"
}
```

### Ответ

Успешный ответ приходит с кодом `200 OK` без содержания тела.

## Метод history_transactions принимает наименование пользователя и возвращает историю транзакцию.

`GET /transactions/` - возвращает история транзакций.

Параметры:

* `user_id` – пользователь
* `sort` – сортировка транзакций по сумме-`amount` или времени создания-`create_time`
* `reverse` – "True" по убыванию, "False" или не указывать значение по увеличению

### Пример запроса

`GET /transactions/?user_id=12&sort=amount&reverse=True

### Ответ

Успешный ответ приходит с кодом `200 OK` и содержит тело:

```json
[
  {
    "amount": 1000.0,
    "comment": "Пополнение",
    "create_time": "Fri, 06 May 2022 10:16:43 GMT",
    "id": 7,
    "type": "Начисление",
    "user_id": "12"
  },
  {
    "amount": 1000.0,
    "comment": "Пополнение",
    "create_time": "Fri, 06 May 2022 10:16:46 GMT",
    "id": 8,
    "type": "Начисление",
    "user_id": "12"
  },
  {
    "amount": 1000.0,
    "comment": "Перевод",
    "create_time": "Fri, 06 May 2022 10:55:38 GMT",
    "id": 12,
    "type": "Списание переводом",
    "user_id": "12"
  },
  {
    "amount": 500.0,
    "comment": "Покупка утюга",
    "create_time": "Fri, 06 May 2022 10:52:09 GMT",
    "id": 11,
    "type": "Списание",
    "user_id": "12"
  }
]
```