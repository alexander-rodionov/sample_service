from abc import abstractmethod
from logging import Logger, StreamHandler, INFO, DEBUG, WARNING, ERROR, CRITICAL, Formatter, Handler
from logging.handlers import RotatingFileHandler
from typing import Optional
from ..misc import LazyValue

from ..abc import ModuleABC

DEFAULT_LOG_DIR = './logs'
DEFAULT_LOG_FILENAME = 'log.log'
LOG_FORMAT = '%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s'
DEFAULT_LOG_LEVEL = INFO
DEFAULT_LOG_SIZE = 10 ** 4
DEFAULT_LOG_COUNT = 10


class LoggerABC:
    @abstractmethod
    def debug(self, source, *args):
        pass

    @abstractmethod
    def info(self, source, *args):
        pass

    @abstractmethod
    def warn(self, source, *args):
        pass

    @abstractmethod
    def err(self, source, *args):
        pass


class LoggerModule(ModuleABC, LoggerABC):
    """Отвечает за логирование и ротацию логов"""

    def __init__(self, workfolder: LazyValue = LazyValue(DEFAULT_LOG_DIR),
                 loglevel: LazyValue = LazyValue(DEFAULT_LOG_LEVEL),
                 rotating_size_bytes: LazyValue = LazyValue(DEFAULT_LOG_SIZE),
                 backup_count: LazyValue = LazyValue(DEFAULT_LOG_COUNT),
                 config=None):
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
        LoggerABC.__init__(self)
        ModuleABC.__init__(self)

        self.workfolder = workfolder
        self.loglevel = loglevel
        self.rotating_size_bytes = rotating_size_bytes
        self.backup_count = backup_count
        self.logger: Optional[Logger] = None
        self.config = config

    async def start(self) -> None:
        log_levels = {
            'DEBUG': DEBUG,
            'INFO': INFO,
            'WARNING': WARNING,
            'ERROR': ERROR,
            'CRITICAL': CRITICAL
        }
        int_log_level = log_levels[self.loglevel()]

        self.logger = Logger('main_logger')
        self.logger.setLevel(int_log_level)
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter(LOG_FORMAT))
        console_handler.setLevel(int_log_level)
        self.logger.addHandler(console_handler)

        file_logger = RotatingFileHandler(filename=f"{self.workfolder()}/{DEFAULT_LOG_FILENAME}", mode='a',
                                          encoding='utf-8', backupCount=self.backup_count(),
                                          maxBytes=self.rotating_size_bytes())
        file_logger.setLevel(self.loglevel())
        file_logger.setFormatter(Formatter(LOG_FORMAT))
        self.logger.addHandler(file_logger)
        self.welcome()
        self.info(self, 'Logger started')

    @property
    def _welcome_log_message(self) -> str:
        m = '\n' + '-' * 80 + '\n'
        m += 'Starting currency converter service with config:\n'
        m += self.config.dump + '\n'
        m += '-' * 80
        return m

    def stop(self) -> None:
        assert self.logger
        self.info(self, 'Logger stopped')
        h: Handler
        for h in self.logger.handlers:
            h.flush()

    async def run(self) -> None:
        ...

    @staticmethod
    def _call_with_args(method, *args) -> None:
        method(' '.join([str(x) for x in args]).replace('\t', ' '))

    def debug(self, source, *args) -> None:
        assert self.logger
        self._call_with_args(self.logger.debug, source.__class__.__name__ if source else 'UnknownSource', *args)

    def info(self, source, *args) -> None:
        assert self.logger
        self._call_with_args(self.logger.info, source.__class__.__name__ if source else 'UnknownSource', *args)

    def warn(self, source, *args) -> None:
        assert self.logger
        self._call_with_args(self.logger.warning, source.__class__.__name__ if source else 'UnknownSource', *args)

    def err(self, source, *args) -> None:
        assert self.logger
        self._call_with_args(self.logger.error, source.__class__.__name__ if source else 'UnknownSource', *args)

    def welcome(self) -> None:
        assert self.logger
        self.logger.info(self._welcome_log_message)
