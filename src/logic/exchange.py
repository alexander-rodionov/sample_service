from abc import ABC, abstractmethod
from asyncio import Queue, Event, wait_for
from dataclasses import dataclass
from typing import Union, Callable, Dict, List, Optional
from ..abc import LoggerABC
from ..misc import id_gen

EXCHANGE_CALL_TIMEOUT = 10  # sec

class ServiceExchangeABC(ABC):
    @abstractmethod
    async def call(self, target: str, data: Union[Dict, List]):
        ...

    @abstractmethod
    def register_client(self, target: str, handler: Callable):
        ...


@dataclass
class QueueMessage:
    id: str
    target: str
    data: Union[Dict, List]

class ServiceExchange(ServiceExchangeABC):
    def __init__(self, log: LoggerABC):
        ServiceExchangeABC.__init__(self)
        self.request_queue = Queue()
        self.response_queue = Queue()
        self.events: Dict[str, Event] = {}
        self.clients = {}
        self.log = log

    async def call(self, target: str, data: Union[Dict, List]):
        event = Event()
        id = id_gen()
        msg = QueueMessage(id=id_gen(), target=target, data=data)
        self.events[id] = event
        await self.request_queue.put(msg)
        try:
            await wait_for(event.wait(), timeout=EXCHANGE_CALL_TIMEOUT)
        except TimeoutError:
            self.log.warn(self, f'Exchange call {id} timed out')
            del self.events[id]
            return None
        return await self.response_queue.get()

    def register_client(self, target: str, handler: Callable):
        self.clients[target] = handler

    async def run(self):
        while True:
            msg = await self.queue.get()
            if msg.target in self.clients:
                result = await self.clients[msg.target](msg.data)
                msg.event.set()
                if result is not None:
                    await self.call(msg.target, result)

            self.log.warn(self, f'Client {msg.target} not found, throwing message away')