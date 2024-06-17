from asyncio import sleep
from typing import Optional, List, Type

from .. import ServiceExchangeABC, LoggerABC, ModuleABC
from aiohttp.web import Application, AppRunner, TCPSite
from .api_handler import ApiHandlerABC

LONG_SLEEP_TIME = 3600

class HttpServerModule(ModuleABC):
    def __init__(self, exchange: ServiceExchangeABC, log: LoggerABC, handler_types: List[Type[ApiHandlerABC]], host, port):
        self.exchange = exchange
        self.log = log
        self.app: Optional[Application] = None
        self.site = None
        self.host = host
        self.port = port
        self.handler_types = handler_types
        self.handlers = None


    async def start(self):
        self.log.info(self, 'Starting HTTP server')
        self.app = Application()
        self.handlers = [h(self.app, self.exchange, self) for h in self.handler_types]

    def stop(self):
        self.log.info(self, 'Stopping HTTP server')

    async def run(self):
        runner = AppRunner(self.app)
        await runner.setup()
        self.site = TCPSite(runner, host=self.host(), port=self.port())
        await self.site.start()
        self.log.info(self, 'HTTP server started')

        while True:
            await sleep(LONG_SLEEP_TIME)

