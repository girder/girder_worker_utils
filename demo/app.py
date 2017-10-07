from celery import Celery, Task
from girder_worker_utils.serializer import deserialize, serialize
from kombu.serialization import register


class CustomTask(Task):
    def __call__(self, *args, **kwargs):
        def _t(arg):
            try:
                return arg.transform()
            except AttributeError:
                return arg

        return self.run(*[_t(a) for a in args], **kwargs)


# Register the custom serializer with kombu
register('girder_io', serialize, deserialize,
         content_type='application/json',
         content_encoding='utf-8')

app = Celery('proj',
             broker='amqp://',
             backend='amqp://',
             include=['tasks'],
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
