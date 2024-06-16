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


class DataProviderModule(ModuleABC):
    def __init__(self, api_key: str, log: LoggerABC, cache_ttl, dump_file):
        self.data_loader = None
        self.api_key = api_key
        self.log = log
        self.cache_ttl = cache_ttl
        self.dump_file = dump_file

    async def start(self):
        self.data_loader = CachedDataLoader(api_key=self.api_key, log=self.log,
                                            cache_ttl=self.cache_ttl, dump_file=self.dump_file)

    async def run(self):
        ...

    def stop(self):
        ...
