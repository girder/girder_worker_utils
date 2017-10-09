from gw_utils_demo_app import tasks
from gw_utils_demo_app.transform import RaiseException, Reverse


# tasks.task.delay('foobar')
print(tasks.task(Reverse('foobar')))
print(tasks.task.delay('foobar').get())
print(tasks.task.delay(Reverse('foobar')).get())
print(tasks.task.delay(RaiseException()).get())
