from girder_worker_utils.transform import RaiseException, Reverse

import tasks

# tasks.task.delay('foobar')
print(tasks.task(Reverse('foobar')))
print(tasks.task.delay('foobar').get())
print(tasks.task.delay(Reverse('foobar')).get())
print(tasks.task.delay(RaiseException()).get())
