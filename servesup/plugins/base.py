import abc
from tornado import httputil


class Plugin(abc.ABC):
    @abc.abstractmethod
    def response(self, request: httputil.HTTPServerRequest) -> str:
        pass
