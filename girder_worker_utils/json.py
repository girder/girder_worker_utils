from __future__ import absolute_import

from functools import wraps

import json


_hook_registry = {}


def register_hook(name, func, *args, **kwargs):
    _hook_registry[name] = func, args, kwargs


def hook(name, *args, **kwargs):
    def decorator(func):
        register_hook(name, func, *args, **kwargs)
        return func
    return decorator


class JSONDecoder(json.JSONDecoder):
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        return super(JSONEncoder, self).default(o)


def object_hook(data):
    hook_definition = _hook_registry.get(data.get('__json_hook__'))
    if hook_definition:
        hook, args, kwargs = hook_definition
        args = args + (data,)
        return hook(*args, **kwargs)
    return data


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
