from random import randint
from plugins.base import Plugin


class MyResponse(Plugin):
    def response(self):
        return f"Dynamic response {randint(0,10)}"
