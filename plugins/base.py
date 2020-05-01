import abc


class Plugin(abc.ABC):
    @abc.abstractmethod
    def response(self):
        pass
