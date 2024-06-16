from src import LoggerModule, ConfigModule, Launcher, HttpServerModule, ServiceExchange, DataProviderModule, CurrencyAPI


config = ConfigModule()
logger = LoggerModule(
    workfolder=config.lazy('logger.workfolder'),
    loglevel=config.lazy('logger.loglevel'),
    rotating_size_bytes=config.lazy('logger.rotating_size_bytes'),
    backup_count=config.lazy('logger.backup_count')
)
exchange = ServiceExchange(logger)
http_server = HttpServerModule(exchange, logger, [CurrencyAPI], config.lazy('http.host'), config.lazy('http.port'))
data_provider = DataProviderModule(
    config.lazy('data_provider.api_key'),
    logger,
    config.lazy('data_provider.cache_ttl'),
    config.lazy('data_provider.dump_file')
)

Launcher([
    config,
    logger,
    data_provider,
    http_server
]).run()



