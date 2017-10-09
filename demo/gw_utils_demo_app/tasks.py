from app import app


@app.task
def task(string):
    return string
