from src import LoggerModule, ConfigModule, Launcher, HttpServerModule, ServiceExchangeModule, DataProviderModule, \
    CurrencyAPI

config = ConfigModule()
logger = LoggerModule(
    workfolder=config.lazy('logger.workfolder'),
    loglevel=config.lazy('logger.loglevel'),
    rotating_size_bytes=config.lazy('logger.rotating_size_bytes'),
    backup_count=config.lazy('logger.backup_count'),
    config=config
)
exchange = ServiceExchangeModule(logger)
http_server = HttpServerModule(
    exchange=exchange,
    log=logger,
    handler_types=[CurrencyAPI],
    host=config.lazy('http.host'),
    port=config.lazy('http.port')
)
data_provider = DataProviderModule(
    logger,
    exchange,
    config.lazy('data_provider.api_key'),
    config.lazy('data_provider.cache_ttl'),
    config.lazy('data_provider.dump_file')
)

Launcher([
    config,
    logger,
    exchange,
    data_provider,
    http_server
]).run()
