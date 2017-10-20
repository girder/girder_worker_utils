import os
import tempfile

from girder_client import GirderClient
from six.moves import cStringIO

from ..transform import Transform


class GirderTransform(Transform):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.client = kwargs.get('client')

        if args:
            self.value = args[0]

        if not self.client and kwargs.get('api_url'):
            self.client = GirderClient(apiUrl=kwargs['api_url'])

        if not self.client:
            raise Exception('GirderTransform requires a girder client instance or api url')

        if kwargs.get('token'):
            self.client = kwargs['token']

    def get_prefix(self):
        if not self.kwargs.get('prefix'):
            self.kwargs['prefix'] = tempfile.mkdtemp(prefix='girder_worker_utils')
        return self.kwargs['prefix']


class GirderFileToString(GirderTransform):
    def transform(self):
        f = cStringIO()
        self.client.downloadFile(self.value, f)
        return f.getvalue()


class GirderFileToFileObject(GirderTransform):
    def transform(self):
        f = cStringIO()
        self.client.downloadFile(self.value, f)
        return f


class GirderFileToLocalFile(GirderTransform):
    def transform(self):
        file_name = self.kwargs.get('file_name')
        if not file_name:
            file_name = self.client.getFile(self.value)['name']
        file_path = os.path.join(self.get_prefix(), file_name)
        self.client.downloadFile(self.value, file_path)
        return file_path
