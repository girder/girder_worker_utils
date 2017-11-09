from __future__ import absolute_import

from functools import wraps

import importlib
import json
import six

# Singleton/ClassVariableSingleton.py
class Hook(object):
    """Deserialize objects with __class_hint__ attributes.

    This class abstracts over the process of turning a json dictionary
    into an instantiated object.  It does this by accepting a string
    keyword argument for the module and function that constructs the
    object. You may optionally pass in class if the object constructor
    is a classmethod.

    """

    def __init__(self, func=None, module=None, cls=None, **kwargs):
        module = importlib.import_module(module)

        if cls is not None:
            cls = getattr(module, cls)
            self.func = getattr(cls, func)
        else:
            self.func = getattr(module, func)

        assert hasattr(self.func, '__call__'), \
            'Object deserialization function must be callable!'

    def construct(self, data):
        """Construct the object.

        Call the object constructor after removing __class_hint__ from
        the object data.
        """
        data.pop('__class_hint__')
        return self.func(data)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        return super(JSONEncoder, self).default(o)


def object_hook(data):
    """Object hook passed to the JSONDecoder."""
    try:
        return Hook(**data['__class_hint__']).construct(data)
    except Exception:
        return data


class JSONDecoder(json.JSONDecoder):
    pass


@wraps(json.load)
def load(*args, **kwargs):
    kwargs.setdefault('object_hook', object_hook)
    return json.load(*args, **kwargs)


@wraps(json.loads)
def loads(*args, **kwargs):
    kwargs.setdefault('object_hook', object_hook)
    return json.loads(*args, **kwargs)


@wraps(json.dump)
def dump(*args, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return json.dump(*args, **kwargs)


@wraps(json.dumps)
def dumps(*args, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return json.dumps(*args, **kwargs)
