from abc import ABC, abstractmethod
from asyncio import Queue, Event, wait_for
from dataclasses import dataclass
from typing import Union, Callable, Dict, List, Optional, Any
from ..abc import LoggerABC, ModuleABC
from ..misc import id_gen
from asyncio.exceptions import TimeoutError as AsyncTimeoutError

EXCHANGE_CALL_TIMEOUT = 6000  # sec


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


class ServiceExchangeModule(ServiceExchangeABC, ModuleABC):
    def __init__(self, log: LoggerABC):
        ServiceExchangeABC.__init__(self)
        self.request_queue: Queue = Queue()
        self.results: Dict[str, Any] = {}
        self.events: Dict[str, Event] = {}
        self.clients: Dict[str, Callable] = {}
        self.log = log

    async def call(self, target: str, data: Union[Dict, List]):
        self.log.debug(self, f'Calling {target} with {data}')
        event = Event()
        id = id_gen()
        msg = QueueMessage(id=id, target=target, data=data)
        self.events[id] = event
        self.results[id] = None
        await self.request_queue.put(msg)
        try:
            await wait_for(event.wait(), timeout=EXCHANGE_CALL_TIMEOUT)
            result = self.results[id]
            if isinstance(result, Exception):
                raise result
        except AsyncTimeoutError:
            self.log.warn(self, f'Exchange call {id} timed out')
            result = None
        except Exception as e:
            self.log.err(self, f'Error calling {target}: {e}')
            raise e
        finally:
            del self.events[id]
            del self.results[id]
        return result

    def register_client(self, target: str, handler: Callable):
        self.clients[target] = handler

    async def run(self):
        while True:
            msg = await self.request_queue.get()
            if msg.target in self.clients:
                try:
                    self.results[msg.id] = await self.clients[msg.target](msg.data)
                except Exception as e:
                    self.results[msg.id] = e
                finally:
                    self.events[msg.id].set()
            else:
                self.log.warn(self, f'Client {msg.target} not found, throwing message away')
            self.log.debug(self,
                           f'events_len: {len(self.events)}, results_len: {len(self.results)}, queue_len: {self.request_queue.qsize()}')

    async def start(self):
        ...

    def stop(self):
        ...
