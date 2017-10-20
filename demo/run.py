import json

from girder_worker_utils.transform import Transform
from girder_worker_utils.transforms import girder
from gw_utils_demo_app import tasks
from gw_utils_demo_app.transform import RaiseException, Reverse

api_url = 'https://data.kitware.com/api/v1'

# tasks.task.delay('foobar')
print(tasks.task(Transform('foobar')))
print(tasks.task(Reverse('foobar')))
print(tasks.task.delay('foobar').get())
print(tasks.task.delay(Reverse('foobar')).get())

print(girder.GirderFileToString('55c8998f8d777f6ddc3ff818', api_url=api_url).transform()[:35])
data = json.loads(tasks.task.delay(
    girder.GirderFileToString('55c8998f8d777f6ddc3ff818', api_url=api_url)
).get())
print(data.keys())

data = tasks.task.delay(
    girder.GirderFileToFileObject('55c8998f8d777f6ddc3ff818', api_url=api_url)
).get()
print(data)

data = tasks.task.delay(
    girder.GirderFileToLocalFile('55c8998f8d777f6ddc3ff818', api_url=api_url)
).get()
print(data)

print(tasks.task.delay(RaiseException()).get(propagate=False))
