'''
Задание звучит как написать сервис Конвертер валют, который работает по REST-API.
Пример запроса:
GET /api/rates?from=USD&to=RUB&value=1
Ответ:
{
    "result": 62.16
}
'''
from asyncio import Queue

from ..abc import ModuleABC, LoggerABC
from .data_loader import CachedDataLoader


class DataProviderIncorrectKey(Exception):
    ...

class DataProviderModule(ModuleABC):
    def __init__(self, log: LoggerABC, exchange, api_key: str,  cache_ttl, dump_file):
        self.data_loader = None
        self.exchange = exchange
        self.api_key = api_key
        self.log = log
        self.cache_ttl = cache_ttl
        self.dump_file = dump_file

    async def start(self):
        self.data_loader = CachedDataLoader(api_key=self.api_key, log=self.log,
                                            cache_ttl=self.cache_ttl, dump_file=self.dump_file)
        self.exchange.register_client(target='get_list', handler=self.get_list)
        self.exchange.register_client(target='convert', handler=self.convert)

    async def run(self):
        ...

    def stop(self):
        self.log.info(self, 'Data provider stopped')

    async def convert(self, inp):
        p_from = inp['from_currency']
        p_to = inp['to_currency']
        p_value = inp['value']
        data = await self.data_loader.get_data()
        try:
            result = data.data[p_from][p_to] * p_value
        except KeyError:
            raise DataProviderIncorrectKey(f'Cannot convert {p_from} to {p_to}')
        return result

    async def get_list(self, inp):
        assert self.data_loader
        data = await self.data_loader.get_data()
        return list(data.data.keys())

