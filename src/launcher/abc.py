from abc import ABC, abstractmethod


class ModuleABC(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    async def stop(self):
        ...

    @abstractmethod
    async def run(self):
        ...
