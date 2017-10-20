import functools

from celery import Celery, Task
from kombu.serialization import register
from kombu.utils import json

from girder_worker_utils.json import object_hook


class CustomTask(Task):
    def __call__(self, *args, **kwargs):
        def _t(arg):
            if hasattr(arg, 'transform'):
                return arg.transform()
            return arg

        return self.run(*[_t(a) for a in args], **kwargs)


def serialize(obj):
    if hasattr(obj, '__json__'):
        obj = obj.__json__()
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
             include=['gw_utils_demo_app.tasks', 'girder_worker_utils.transforms.girder'],
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
