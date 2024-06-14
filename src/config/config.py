from enum import Enum
from functools import reduce

from yaml import safe_load
from .. import ModuleABC
from ..misc import LazyValue


class ConfigSource(Enum):
    ENV = 'env'
    FILE = 'file'

DEFAULT_CONFIG_PATH = './config/config.yaml'
DEFAULT_CONFIG_SOURCE = ConfigSource.ENV

class ConfigModule(ModuleABC):
    def __init__(self, config_file: str = DEFAULT_CONFIG_PATH, config_source: ConfigSource = DEFAULT_CONFIG_SOURCE):
        self.config = None
        self.config_file = config_file
        self.config_source = config_source

    async def start(self):
        try:
            with open(self.config_file) as f:
                self.config = safe_load(f)
        except Exception as e:
            print(f'Error loading config file {self.config_file}: {e}')
            raise e

    async def stop(self):
        ...

    def __getitem__(self, item : str):
        assert self.config
        val = self.config
        #return reduce(lambda a, x:, item.split('.'), val)
        #for sub_item in item.split('.'):
        #    val = val[sub_item]


        return self.config[item]

    def lazy(self, item):
        return LazyValue(lambda: self.__getitem__(item))

    async def run(self):
        ...