import functools

from kombu.utils import json
from stevedore.driver import DriverManager


def get_transform_class(name):
    return DriverManager(
        namespace='girder.worker.transform',
        name=name
    ).driver


def object_hook(obj):
    if '_class' not in obj:
        return obj

    cls = get_transform_class(obj['_class'])
    return cls.__obj__(obj["__state__"])


def serialize(obj):
    return json.dumps(obj, check_circular=False)


def deserialize(obj):
    return json.loads(
        obj, _loads=functools.partial(
            json.json.loads, object_hook=object_hook))
