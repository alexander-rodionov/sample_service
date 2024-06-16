from enum import Enum
from functools import reduce

from yaml import safe_load
from .. import ModuleABC
from ..misc import LazyValue


DEFAULT_CONFIG_PATH = './config/config.yaml'

class ConfigModule(ModuleABC):
    def __init__(self, config_file: str = DEFAULT_CONFIG_PATH):
        self.config = None
        self.config_file = config_file

    async def start(self):
        try:
            with open(self.config_file) as f:
                self.config = safe_load(f)
        except Exception as e:
            print(f'Error loading config file {self.config_file}: {e}')
            raise e

    def stop(self):
        ...

    def __getitem__(self, item : str):
        assert self.config
        val = self.config
        try:
            value = reduce(lambda a, x: a[x], item.split('.'), val)
        except KeyError:
            raise Exception(f'Key {item} not found in config file {self.config_file}')
        return value

    def lazy(self, item):
        return LazyValue(lambda: self.__getitem__(item))

    async def run(self):
        ...
