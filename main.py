from src import LoggerModule, ConfigModule, Launcher

config = ConfigModule()
logger = LoggerModule(
    workfolder=config.lazy('logger.workfolder'),
    loglevel=config.lazy('logger.loglevel'),
    rotating_size_bytes=config.lazy('logger.rotating_size_bytes'),
    backup_count=config.lazy('logger.backup_count')
)

l = Launcher([
    logger,
    config
])

l.run()


