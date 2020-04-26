import json
import handler


class Config:
    def __init__(self, file_path):
        with open(file_path, "r") as file:
            self._conf = json.load(file)
        self._routes = self._conf.get("routes")
        self._handlers = [
            (
                route.get("path"),
                handler.CustomHandler,
                dict(handler_opts=route.get("handler_opts"))
            ) for route in self._routes
        ]

    @property
    def routes(self):
        return self._routes

    @property
    def handlers(self):
        # [(r"/", MainHandler, dict(conf={"body": "adsasdasd"})),]
        return self._handlers
