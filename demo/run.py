import json

from girder_worker_utils.transform import Transform
from gw_utils_demo_app import tasks
from gw_utils_demo_app.transform import GirderFile, RaiseException, Reverse


# tasks.task.delay('foobar')
print(tasks.task(Transform('foobar')))
print(tasks.task(Reverse('foobar')))
print(tasks.task.delay('foobar').get())
print(tasks.task.delay(Reverse('foobar')).get())

data = json.loads(tasks.task.delay(GirderFile('55c8998f8d777f6ddc3ff818')).get())
print(data.keys())

print(tasks.task.delay(RaiseException()).get())
