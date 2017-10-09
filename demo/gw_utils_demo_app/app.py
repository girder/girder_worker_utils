import functools
from importlib import import_module

from celery import Celery, Task
from kombu.serialization import register
from kombu.utils import json


class CustomTask(Task):
    def __call__(self, *args, **kwargs):
        def _t(arg):
            try:
                return arg.transform()
            except AttributeError:
                return arg

        return self.run(*[_t(a) for a in args], **kwargs)


def object_hook(obj):
    if '_class' not in obj or '_module' not in obj:
        return obj

    cls = getattr(import_module(obj['_module']), obj['_class'])
    return cls.deserialize(obj['__state__'])


def serialize(obj):
    if hasattr(obj, 'serialize'):
        obj = obj.serialize()
    return json.dumps(obj, check_circular=False)


def deserialize(obj):
    return json.loads(
        obj, _loads=functools.partial(
            json.json.loads, object_hook=object_hook))


# Register the custom serializer with kombu
register('girder_io', serialize, deserialize,
         content_type='application/json',
         content_encoding='utf-8')

app = Celery('proj',
             broker='amqp://',
             backend='amqp://',
             include=['gw_utils_demo_app.tasks'],
             task_cls=CustomTask)

app.conf.update(
    accept_content=['girder_io'],
    result_expires=3600,
    task_serializer='girder_io',
    result_serializer='girder_io',
    worker_send_task_events=True,
    task_send_sent_event=True

)

if __name__ == '__main__':
    app.start()
