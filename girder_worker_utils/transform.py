import inspect


class Transform(object):

    def __init__(self, *args, **kwargs):
        self.value = None
        if args:
            self.value = args[0]

    def __json__(self):
        return self.serialize()

    def serialize(self):
        return {
            '_module': inspect.getmodule(self.__class__).__name__,
            '_class': self.__class__.__name__,
            '__state__': self.__state__
        }

    @classmethod
    def deserialize(cls, state):
        return cls(*state.get('args', []), **state.get('kwargs', {}))

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__state__ = {
            'args': args,
            'kwargs': kwargs
        }
        return obj

    def transform(self):
        return self.value
