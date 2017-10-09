from StringIO import StringIO

from girder_client import GirderClient
from girder_worker_utils.transform import Transform
from kombu.exceptions import DecodeError


class Capitalize(Transform):
    def __init__(self, value):
        self.value = value

    def transform(self):
        return self.value.upper()


class RaiseException(Transform):

    def transform(self):
        raise DecodeError("Some kind of Error")


class Reverse(Transform):
    def __init__(self, value):
        self.value = value

    def transform(self):
        return self.value[::-1]


class GirderFile(Transform):
    def __init__(self, value):
        self.value = value

    def transform(self):
        f = StringIO()
        cl = GirderClient(apiUrl='https://data.kitware.com/api/v1')
        cl.downloadFile(self.value, f)
        return f.getvalue()
