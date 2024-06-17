from enum import Enum
from functools import reduce

from yaml import safe_load
from .. import ModuleABC
from ..misc import LazyValue

DEFAULT_CONFIG_PATH = './config/config.yaml'
DEFAULT_SECRET_PATH = './config/secret.yaml'


class ConfigModule(ModuleABC):
    def __init__(self, config_file: str = DEFAULT_CONFIG_PATH, secret_file: str = DEFAULT_SECRET_PATH):
        self.config = None
        self.config_file = config_file
        self.secret_file = secret_file
        self.config_string_dump = ''

    @property
    def dump(self):
        return self.config_string_dump

    def _make_config_string_dump(self):
        if self.config:
            self.config_string_dump = '\n'.join([f'{k} = {v}' for k, v in self.config.items()])

    @classmethod
    def _deep_update(cls, d, u):
        for k, v in u.items():
            d[k] = cls._deep_update(d.get(k, {}), v) if isinstance(v, dict) else v
        return d

    async def start(self):
        try:
            with open(self.config_file) as f:
                self.config = safe_load(f)
            self._make_config_string_dump()
            with open(self.secret_file) as f:
                self._deep_update(self.config, safe_load(f))
        except Exception as e:
            print(f'Error loading config file {self.config_file}: {e}')
            raise e

    def stop(self):
        ...

    def __getitem__(self, item: str):
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
