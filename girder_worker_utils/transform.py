import abc
import inspect
from . import _walk_obj
from .json import object_hook

import six


@six.add_metaclass(abc.ABCMeta)
class Transform(object):
    def __init__(self, *args, **kwargs):
        pass

    def __json__(self):
        data = self.serialize()
        data = _walk_obj(data, lambda o: o.__json__() if hasattr(o, '__json__') else o)

        data['__class_hint__'] = {
            'module': inspect.getmodule(self.__class__).__name__,
            'cls': self.__class__.__name__,
            'func': 'deserialize'
        }

        return data

    def model_repr(self):
        """
        This method is called before save the argument in the job model.
        """
        return str(self)

    def cleanup(self):
        pass

    @staticmethod
    def _class_hintp(o):
        try:
            o['__class_hint__']; return True # noqa
        except Exception:
            return False

    @classmethod
    def deserialize(cls, data):
        self = cls.__new__(cls)
        self.__dict__ = _walk_obj(data, object_hook, leaf_condition=cls._class_hintp)
        return self

    def serialize(self):
        return self.__dict__

    @abc.abstractmethod
    def transform(self):
        pass
