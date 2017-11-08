import abc
import inspect

import six


@six.add_metaclass(abc.ABCMeta)
class Transform(object):
    def __init__(self, *args, **kwargs):
        pass

    def __json__(self):
        data = self.serialize()
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

    @classmethod
    def deserialize(cls, data):
        self = cls.__new__(cls)
        self.__dict__ = data
        return self

    def serialize(self):
        return self.__dict__

    @abc.abstractmethod
    def transform(self):
        pass
