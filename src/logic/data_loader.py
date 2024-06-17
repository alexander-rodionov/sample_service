import json
import os.path
from asyncio import CancelledError
from dataclasses import dataclass
from itertools import product
from datetime import datetime
from typing import Dict, Optional, Type
from ..abc import LoggerABC
from ..misc import LazyValue

from aiohttp import TCPConnector, ClientSession
DEFAULT_CURRENCY_API_URL = 'https://api.freecurrencyapi.com'
DEFAULT_CURRENCY_METHOD = '/v1/latest'
DEFAULT_CASH_TTL = 60  # sec
DEFAULT_CACHE_DUMP_FILE = './cache/cross_rates.json'


@dataclass
class DataResult:
    data: Optional[Dict[str, Dict[str, float]]]
    status: Optional[int]
    exception_class: Optional[Type[Exception]]
    excexption_message: Optional[str]


class DataLoader:
    def __init__(self, api_key: str, log: LoggerABC):
        self.api_key = api_key
        self.log = log
        self.conn = TCPConnector(ssl=False, limit=20)

    def __del__(self):
        self.conn.close()

    async def _load_from_api(self):
        url = f'{DEFAULT_CURRENCY_API_URL}{DEFAULT_CURRENCY_METHOD}'
        params = {'apikey': self.api_key}
        async with ClientSession(connector=self.conn) as session:
            async with session.get(url, params=params) as resp:
                status = resp.status
                body = await resp.json()
                self.log.info(self, f'Requesting {url} -> status: {status}')
        return body, status

    def _make_cross_table(self, data):
        rates = data['data']
        cross_table = [(k1, k2, float(rates[k2]) / float(rates[k1])) for k1, k2 in product(rates, repeat=2)]
        result = {}
        for k1, k2, v in cross_table:
            if k1 not in result:
                result[k1] = {k2: v}
            else:
                result[k1][k2] = v
        return result

    async def get_data(self):
        try:
            data, status = await self._load_from_api()
            cross_table = self._make_cross_table(data)
            return DataResult(cross_table, status, None, None)
        except CancelledError as e:
            self.log.info(self, 'Task cancelled')
            raise e
        except Exception as e:
            self.log.err(self, f'Error loading data: {e}')
            return DataResult(None, None, type(e), str(e))


class CachedDataLoader(DataLoader):
    def __init__(self, api_key: LazyValue, log: LoggerABC,
                 cache_ttl = LazyValue(DEFAULT_CASH_TTL),
                 dump_file = LazyValue(DEFAULT_CACHE_DUMP_FILE)):
        DataLoader.__init__(self, api_key(), log)
        self.data: Optional[DataResult] = None
        self.cache_ttl = cache_ttl
        self.dump_file = dump_file
        self.timestamp = datetime(1900, 1, 1)
        self._pick_cache()

    def _dump_cache(self):
        self.timestamp = datetime.now()
        cache_data = dict(cross_table=self.data.data, status=self.data.status,
                          timestamp=self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"))
        with open(self.dump_file(), 'w') as f:
            json.dump(cache_data, f)

    def _pick_cache(self):
        if not os.path.exists(self.dump_file()):
            return
        self.log.info(self, f'Loading cache from {self.dump_file()}')
        try:
            with open(self.dump_file(), 'r') as f:
                cache_data = json.load(f)
            self.data = DataResult(cache_data['cross_table'], cache_data['status'], None, None)
            self.timestamp = datetime.fromisoformat(cache_data['timestamp'])
        except Exception as e:
            self.log.warn(self, f'Error loading cache: {e}')
        finally:
            ...

    def __del__(self):
        DataLoader.__del__(self)

    async def get_data(self):
        if (self.data is not None
                and (datetime.now() - self.timestamp).total_seconds() < self.cache_ttl()):
            self.log.debug(self, 'Using cached data')
            return self.data
        else:
            self.data = await super().get_data()
            self._dump_cache()
            return self.data

