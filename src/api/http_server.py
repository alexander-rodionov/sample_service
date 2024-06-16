from asyncio import sleep
from typing import Optional, List, Type

from .. import ServiceExchangeABC, LoggerABC, ModuleABC
from aiohttp.web import Application, AppRunner, TCPSite
from .api_handler import ApiHandlerABC

LONG_SLEEP_TIME = 3600

class HttpServerModule(ModuleABC):
    def __init__(self, exchange: ServiceExchangeABC, log: LoggerABC, handlers: List[Type[ApiHandlerABC]], host, port):
        self.exchange = exchange
        self.log = log
        self.app: Optional[Application] = None
        self.site = None
        self.host = host
        self.port = port
        self.handlers = [h(self.app) for h in handlers]

    async def start(self):
        self.log.info(self, 'Starting HTTP server')
        self.app = Application()

    def stop(self):
        self.log.info(self, 'Stopping HTTP server')

    async def run(self):
        runner = AppRunner(self.app)
        await runner.setup()
        self.site = TCPSite(runner, host=self.host, port=self.port)
        await self.site.start()
        self.log.info(self, 'HTTP server started')
        await self.site.start()

        while True:
            await sleep(LONG_SLEEP_TIME)

