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
from marshmallow.validate import Length, Regexp
from ..abc import DataProviderIncorrectKey

_API_PREFIX = '/api'

class RateSchema(Schema):
    from_currency = fields.String(data_key='from', required=True,
        validate = [
            Length(equal=3, error="from must be exactly 3 characters long"),
            Regexp(regex=r"^[A-Z]{3}$", error="from must consist of uppercase letters A-Z only")
        ]
    )
    to_currency = fields.String(data_key='to',required=True,
        validate = [
            Length(equal=3, error="to must be exactly 3 characters long"),
            Regexp(regex=r"^[A-Z]{3}$", error="to must consist of uppercase letters A-Z only")
        ]
)
    value = fields.Float(required=True, validate=validate.Range(min=0))


class CurrencyAPI(ApiHandlerABC):
    def __init__(self, app, exchange, server):
        ApiHandlerABC.__init__(self, app, exchange, server)

    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/rates')
    async def get_currencies(self, request):
        try:
            schema = RateSchema()
            data = schema.load(request.query)
        except ValidationError as err:
            return json_response({"error": err.messages}, status=400)

        try:
            result = await self.exchange.call('convert', data)
        except DataProviderIncorrectKey as e:
            return json_response({"error": str(e)}, status=400)

        return json_response({"result": result})

    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/rates/list')
    async def get_list(self, request):
        result = await self.exchange.call('get_list', [])
        return json_response(dict(result=result))


    @ApiHandlerABC.api(APIMethods.GET, f'{_API_PREFIX}/heartbeat')
    async def get_heartbeat(self, request):
        return json_response({})

