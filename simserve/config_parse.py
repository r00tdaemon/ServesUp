import sys
import json
from simserve import handler


class Config:
    def __init__(self, file_path):
        try:
            with open(file_path, "r") as file:
                self._conf = json.load(file)
        except FileNotFoundError:
            print(f"Can not find the config file {file_path}.")
            sys.exit(-1)

        self._port = self._conf.get("port")
        self._routes = self._conf.get("routes")
        self._handlers = [
            (
                route.get("path"),
                handler.CustomHandler,
                dict(handler_opts=route.get("handler_opts"))
            ) for route in self._routes
        ]

    @property
    def port(self):
        return self._port

    @property
    def routes(self):
        return self._routes

    @property
    def handlers(self):
        return self._handlers
