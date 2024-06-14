import asyncio


class Launcher:
    def __init__(self, modules: list = []):
        self.modules = modules
        self.loop = asyncio.get_event_loop()

    async def start_all(self):
        for m in self.modules:
            await m.start()

    async def stop_all(self):
        for m in self.modules:
            await m.stop()

    async def _run_inner(self):
        ...

    def run(self):
        self.loop.run_until_complete(self._run_inner())

