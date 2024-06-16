from abc import ABC

from aiohttp.web import get, post, put, delete, Application
from ..abc import ServiceExchangeABC

class APIMethods:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

_route_functions = {
    APIMethods.GET: get,
    APIMethods.POST: post,
    APIMethods.PUT: put,
    APIMethods.DELETE: delete
}
class ApiHandlerABC(ABC):

    def __init__(self, app: Application, exchange: ServiceExchangeABC):
        self.app = app
        self.exchange = exchange
        routes = []
        for m in [m for m in dir(self) if callable(getattr(self, m))]:
            if hasattr(getattr(self, m), 'api_def'):
                method = getattr(self, m)
                method_type, path = method.api_def
                routes.append(_route_functions[method_type](path, method))
        self.app.add_routes(routes)

    @staticmethod
    def api(method_type, path):
        def decorator(func):
            setattr(func, 'api_def', (method_type, path))
            return func
        return decorator

