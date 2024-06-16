import asyncio
from asyncio import all_tasks, current_task, sleep, CancelledError
from signal import SIGTERM, SIGINT, SIGHUP
from typing import List
from .abc import ModuleABC

SHUTDOWN_DOWNCOUNTER = 5
SHUTDOWN_DELAY = 1
LONG_DELAY = 1000


class Launcher:
    def __init__(self, modules: List[ModuleABC]):
        self.modules: List[ModuleABC] = modules
        self.loop = asyncio.get_event_loop()

    async def start_all(self):
        for m in self.modules:
            assert isinstance(m, ModuleABC)
            await m.start()

    def stop_all(self):
        for m in reversed(self.modules):
            assert isinstance(m, ModuleABC)
            m.stop()

    async def _run_inner(self):
        service_stopped = False
        root_task = current_task()
        async def shutdown_task():
            nonlocal service_stopped
            for t in all_tasks():
                if t == current_task() or t.done() or t.cancelled() or t == root_task:
                    continue
                else:
                    t.cancel()
            for _ in range(SHUTDOWN_DOWNCOUNTER):
                tasks_left = [t for t in all_tasks() if
                              (not t.done() and not t.cancelled() and not t == current_task() and not t == root_task)]
                if len(tasks_left) == 0:
                    break
                await sleep(SHUTDOWN_DELAY)
            print('Tasks cancelled')
            self.stop_all()
            print('Modules stopped')
            service_stopped = True
            root_task.cancel()

        def shutdown():
            print('Received signal %s. Shutting down...' % sig)
            self.loop.create_task(shutdown_task())

        for sig in (SIGTERM, SIGINT, SIGHUP):
            self.loop.add_signal_handler(sig, shutdown)
        await self.start_all()
        for m in self.modules:
            assert isinstance(m, ModuleABC)
            self.loop.create_task(m.run())
        try:
            while not service_stopped:
                await sleep(LONG_DELAY)
        except CancelledError:
            pass
        self.loop.stop()
        print('Loop stopped')


    def run(self):
        self.root_task = self.loop.run_until_complete(self._run_inner())
