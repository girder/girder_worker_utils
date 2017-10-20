import importlib
import inspect

from . import json


class Transform(object):

    def __init__(self, *args, **kwargs):
        self.value = None
        if args:
            self.value = args[0]

    def __json__(self):
        return {
            '_module': inspect.getmodule(self.__class__).__name__,
            '_class': self.__class__.__name__,
            '__state__': self.__state__,
            '__json_hook__': 'girder_worker_utils.transform'
        }

    @staticmethod
    @json.hook('girder_worker_utils.transform')
    def deserialize(data):
        module = importlib.import_module(data['_module'])
        cls = getattr(module, data['_class'])
        state = data['__state__']
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
