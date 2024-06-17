from abc import ABC
from typing import Callable, Any, Optional
from typing import TYPE_CHECKING

from aiohttp.web import get, post, put, delete, Application, RouteDef
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

    def __init__(self, app: Application, exchange: ServiceExchangeABC, server):
        self.app = app
        self.exchange = exchange
        self.server = server
        routes = []
        for m in [m for m in dir(self) if callable(getattr(self, m))]:
            if hasattr(getattr(self, m), 'api_def'):
                method = getattr(self, m)
                method_type, path = method.api_def
                method_function = _route_functions[method_type]
                routes.append(method_function(path, method))  # type: ignore
        self.app.add_routes(routes)

    @staticmethod
    def api(method_type, path):
        def decorator(func):
            def wrapper(self, request, *args, **kwargs):
                self.server.log.info(self, f'Request to {path}: {self.request_to_log(request)}')
                return func(self, request, *args, **kwargs)
            setattr(wrapper, 'api_def', (method_type, path))
            return wrapper
        return decorator

    def request_to_log(self, request):
        ip_address = request.transport.get_extra_info("peername")[0]
        user_agent = request.headers.get("User-Agent")
        method = request.method
        path = request.path
        query_string = request.query_string

        return f"{ip_address} - {user_agent} - [{method}] {path}?{query_string}"

