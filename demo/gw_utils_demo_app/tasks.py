import six

from .app import app


@app.task
def task(string):
    if isinstance(string, six.string_types):
        return string
    else:
        return 'received %s' % type(string)
