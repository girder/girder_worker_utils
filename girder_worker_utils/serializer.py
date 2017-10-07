import functools
from importlib import import_module

from kombu.utils import json


def object_hook(obj):
    if '_class' not in obj or '_module' not in obj:
        return obj

    cls = getattr(import_module(obj['_module']), obj['_class'])
    return cls.__obj__(obj["__state__"])


def serialize(obj):
    return json.dumps(obj, check_circular=False)


def deserialize(obj):
    return json.loads(
        obj, _loads=functools.partial(
            json.json.loads, object_hook=object_hook))
