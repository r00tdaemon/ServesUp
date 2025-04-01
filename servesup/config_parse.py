import sys
import json
from servesup import handler


class Config:
    def __init__(self, file_path):
        self.config_file = file_path
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, "r") as file:
                self._conf = json.load(file)
        except FileNotFoundError:
            print(f"Can not find the config file {self.config_file}.")
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

    def reload(self):
        """Reload the configuration from the config file."""
        self._load_config()

    @property
    def port(self):
        return self._port

    @property
    def routes(self):
        return self._routes

    @property
    def handlers(self):
        return self._handlers
