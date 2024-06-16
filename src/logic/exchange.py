from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Union, Callable, Dict, List
from .. import LoggerABC


class ServiceExchangeABC(ABC):
    @abstractmethod
    async def put(self, target:str, data: Union[Dict, List]):
        pass

    @abstractmethod
    def register_client(self, target: str, handler: Callable):
        pass


class ServiceExchange(ServiceExchangeABC):
    def __init__(self, log: LoggerABC):
        ServiceExchangeABC.__init__(self)
        self.queue = Queue()
        self.clients = {}
        self.log = log

    async def put(self, target : str, data: Union[Dict, List]):
        await self.queue.put((target, data))
    def register_client(self, target: str, handler: Callable):
        self.clients[target] = handler

    async def run(self):
        while True:
            target, data = self.queue.get()
            if target in self.clients:
                self.clients[target](data)
            self.log.warn(self, f'Client {target} not found, throwing message away')