import inspect


class Transform(object):

    @classmethod
    def __obj__(cls, state):
        return cls(*state.get('args', []),
                   **state.get('kwargs', {}))

    def __json__(self):
        return {
            '_module': inspect.getmodule(self.__class__).__name__,
            '_class': self.__class__.__name__,
            '__state__': self.__state__
        }

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__state__ = {
            'args': args,
            'kwargs': kwargs
        }
        return obj
