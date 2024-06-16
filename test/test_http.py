from contextlib import contextmanager
from typing import List

import pydantic
import requests
from .config import config

'''
Задание звучит как написать сервис Конвертер валют, который работает по REST-API.
Пример запроса:
GET /api/rates?from=USD&to=RUB&value=1
Ответ:
{
    "result": 62.16
}

Также добавим метод /api/rates/list для получения списка валидных тикеров.
Который возвращает 
['AUD','USD', 'EUR']

Также добавим метод heartbeat для проверки работы сервиса. /api/heartbeat
Возвращает пустой ответ и 200 если сервис поднят

'''

class RatesList(pydantic.BaseModel):
    result: List[str]

class RateResponse(pydantic.BaseModel):
    result: float

def pydantic_check(model, data):
    try:
        model(**data)
    except pydantic.ValidationError as e:
        return False
    return True


_API_PREFIX = '/api'

@contextmanager
def _get(path, params):
    host = config['http']['host']
    port = config['http']['port']
    yield requests.get(f'http://{host}:{port}{_API_PREFIX}/{path}', params=params)

def test_http():
    with _get('heartbeat', {}) as r:
        assert r.status_code == 200

def test_currency_list():
    with _get('rates/list', {}) as r:
        assert r.status_code == 200
        assert pydantic_check(RatesList, r.json())

def test_correct_currency():
    with _get('rates', {'from': 'USD', 'to': 'RUB', 'value': 1}) as r:
        assert r.status_code == 200
        body = r.json()
        assert pydantic_check(RatesList, body)
        assert 70 < body['result'] < 200


def test_incorrect_currency():
    with _get('rates', {'from': 'XYZ', 'to': 'RUB', 'value': 1}) as r:
        assert r.status_code == 400
    with _get('rates', {'from': 'USD', 'to': 'XYZ', 'value': 1}) as r:
        assert r.status_code == 400
