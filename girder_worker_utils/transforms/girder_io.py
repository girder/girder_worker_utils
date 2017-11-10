import os
import shutil
import tempfile

from girder_client import GirderClient

from ..transform import Transform


class GirderClientTransform(Transform):
    def __init__(self, *args, **kwargs):
        gc = kwargs.pop('gc', None)

        try:
            if gc is None:
                from girder.api.rest import getApiUrl, getCurrentToken
                self.gc = GirderClient(apiUrl=getApiUrl())
                self.gc.token = getCurrentToken()['_id']
            else:
                self.gc = gc
        except ImportError:
            self.gc = None


class GirderFileId(GirderClientTransform):
    def __init__(self, _id, **kwargs):
        super(GirderFileId, self).__init__(**kwargs)
        self.file_id = _id

    def model_repr(self):
        return "{}('{}')".format(self.__class__.__name__, self.file_id)

    def transform(self):
        self.file_path = os.path.join(
            tempfile.mkdtemp(), '{}.csv'.format(self.file_id))

        self.gc.downloadFile(self.file_id, self.file_path)

        return self.file_path

    def cleanup(self):
        shutil.rmtree(os.path.dirname(self.file_path),
                      ignore_errors=True)


class GirderItemMetadata(GirderClientTransform):
    def __init__(self, _id, **kwargs):
        super(GirderItemMetadata, self).__init__(**kwargs)
        self.item_id = _id

    def model_repr(self):
        return "{}('{}')".format(self.__class__.__name__, self.item_id)

    def transform(self, data):
        self.gc.addMetadataToItem(self.item_id, data)

        return data


class GirderUploadToItem(GirderClientTransform):
    def __init__(self, _id, delete_file=False, **kwargs):
        super(GirderUploadToItem, self).__init__(**kwargs)
        self.item_id = _id

    def model_repr(self):
        return "{}('{}')".format(self.__class__.__name__, self.item_id)

    def transform(self, path):
        self.output_file_path = path
        self.gc.uploadFileToItem(self.item_id, self.output_file_path)
        return self.item_id

    def cleanup(self):
        if self.delete_file is True:
            shutil.rm(self.output_file_path)
