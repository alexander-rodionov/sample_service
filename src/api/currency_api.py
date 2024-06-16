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
from .api_handler import ApiHandlerABC, APIMethods
from aiohttp.web import json_response
from marshmallow import Schema, fields, validate, ValidationError

_API_PREFIX = '/api'


class RateSchema(Schema):
    from_currency = fields.String(required=True, validate=validate.OneOf(["USD", "EUR", "RUB"]))
    to_currency = fields.String(required=True, validate=validate.OneOf(["USD", "EUR", "RUB"]))
    value = fields.Float(required=True, validate=validate.Range(min=0))


class CurrencyAPI(ApiHandlerABC):
    def __init__(self, app, exchange):
        ApiHandlerABC.__init__(self, app, exchange)

    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/rates')
    async def get_currencies(self, request):
        try:
            schema = RateSchema()
            data = await schema.load(request.query)
        except ValidationError as err:
            return json_response({"error": err.messages}, status=400)

        result = self.exchange.call('something', data['value'])

        return json_response({"result": result})

    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/rates/list')
    def get_currencies(self, request):
        print(request)


    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/heartbeat')
    def get_currencies(self, request):
        print(request)

