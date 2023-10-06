from .app import app


@app.task
def task(string):
    if isinstance(string, str):
        return string
    else:
        return 'received %s' % type(string)
