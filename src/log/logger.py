from logging import Logger, StreamHandler, INFO, Formatter, Handler
from logging.handlers import RotatingFileHandler
from typing import Optional
from ..misc import LazyValue

from .. import ModuleABC

DEFAULT_LOG_DIR = './logs'
LOG_FORMAT = '%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s'
DEFAULT_LOG_LEVEL = INFO
DEFAULT_LOG_SIZE = 10 ** 4
DEFAULT_LOG_COUNT = 10

class LoggerModule(ModuleABC):
    """Отвечает за логирование и ротацию логов"""

    def __init__(self, workfolder: LazyValue = LazyValue(DEFAULT_LOG_DIR),
                 loglevel: LazyValue = LazyValue(DEFAULT_LOG_LEVEL),
                 rotating_size_bytes: LazyValue = LazyValue(DEFAULT_LOG_SIZE),
                 backup_count: LazyValue = LazyValue(DEFAULT_LOG_COUNT)):
        """
        Инициализирует логгер и создает обработчики для консольного и файлового логгера с ротацией

        :param workfolder: путь до рабочей папки
        :type workfolder: str
        :param loglevel: уровень логирования
        :type loglevel: int
        :param rotating_size_bytes: максимальный размер логфайла
        :type rotating_size_bytes: int
        :param backup_count: максимальное количество логфайлов
        :type backup_count: int
        """

        self.workfolder = workfolder
        self.loglevel = loglevel
        self.rotating_size_bytes = rotating_size_bytes
        self.backup_count = backup_count
        self.logger : Optional[Logger] = None

    async def start(self):
        self.logger: Logger = Logger('main_logger')
        self.logger.setLevel(self.loglevel())
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter(LOG_FORMAT))
        console_handler.setLevel(self.loglevel())
        self.logger.addHandler(console_handler)

        file_logger = RotatingFileHandler(filename=f"{self.workfolder()}/log.log", mode='a',
                                          encoding='utf-8', backupCount=self.backup_count(),
                                          maxBytes=self.rotating_size_bytes())
        file_logger.setLevel(self.loglevel())
        file_logger.setFormatter(Formatter(LOG_FORMAT))
        self.logger.addHandler(file_logger)

    async def stop(self):
        assert self.logger
        h: Handler
        for h in self.logger.handlers:
            h.flush()

    async def run(self):
        ...

    @staticmethod
    def _call_with_args(method, *args):
        method(' '.join([str(x) for x in args]).replace('\t', ' '))

    def debug(self, *args):
        assert self.logger
        self._call_with_args(self.logger.debug, *args)

    def info(self, *args):
        assert self.logger
        self._call_with_args(self.logger.info, *args)

    def warn(self, *args):
        assert self.logger
        self._call_with_args(self.logger.warning, *args)

    def err(self, *args):
        assert self.logger
        self._call_with_args(self.logger.error, *args)

