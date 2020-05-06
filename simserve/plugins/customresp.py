from random import randint
from simserve.plugins.base import Plugin


class MyResponse(Plugin):
    def response(self, request):
        return f"Dynamic response {randint(0,10)}"
