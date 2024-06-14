import datetime
from asyncio import CancelledError
from dataclasses import dataclass
from itertools import product
from datetime import datetime
from typing import Dict, Optional, Type, List, Any, Union

from aiohttp import TCPConnector, ClientSession
import asyncio

KEY = 'fca_live_9FJkTt5xA3imhC8GpAhKP7GYbeN34IyqsRDMg8Gs'
DEFAULT_CURRENCY_API_URL = 'https://api.freecurrencyapi.com'
DEFAULT_CURRENCY_METHOD = '/v1/latest'
DEFAULT_CASH_TTL = 60  # seconds


@dataclass
class DataResult:
    data: Optional[List[dict[str, dict[str, float]]]]
    status: Optional[int]
    exception_class: Optional[Type[Exception]]
    excexption_message: Optional[str]


class DataLoader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.conn = TCPConnector(ssl=False, limit=20)

    def __del__(self):
        self.conn.close()

    async def _load_from_api(self):
        url = f'{DEFAULT_CURRENCY_API_URL}/{DEFAULT_CURRENCY_METHOD}'
        params = {'apikey': self.api_key}
        async with ClientSession(connector=self.conn) as session:
            async with session.get(url, params=params) as resp:
                status = resp.status
                body = await resp.json()
        return body, status

    def _make_cross_table(self, data):
        rates = data['data']
        return [{k1: {k2: float(rates[k1]) / float(rates[k2])}} for k1, k2 in product(rates, repeat=2)]

    async def get_data(self):
        try:
            data, status = await self._load_from_api()
            cross_table = self._make_cross_table(data)
            return DataResult(cross_table, status, None, None)
        except CancelledError as e:
            raise e
        except Exception as e:
            return DataResult(None, None, type(e), str(e))


class CachedDataLoader(DataLoader):
    def __init__(self, api_key: str, cache_ttl=DEFAULT_CASH_TTL):
        DataLoader.__init__(self, api_key)
        self.data: Optional[DataResult] = None
        self.cache_ttl = cache_ttl
        self.timestamp = None

    def __del__(self):
        DataLoader.__del__(self)

    async def get_data(self):
        self.data.data['timestamp']
        if self.data is not None and (datetime.now() - self.data.data['timestamp']).total_seconds() < self.cache_ttl:
            return self.data
        else:
            self.data = await super().get_data()
            return self.data


dl = DataLoader(KEY)
