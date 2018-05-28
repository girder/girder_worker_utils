import os
import shutil
import tempfile

from girder_client import GirderClient

from ..transform import ResultTransform, Transform


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


class GirderClientResultTransform(ResultTransform, GirderClientTransform):
    pass


class GirderFileId(GirderClientTransform):
    def __init__(self, _id, **kwargs):
        super(GirderFileId, self).__init__(**kwargs)
        self.file_id = _id

    def _repr_model_(self):
        return "{}('{}')".format(self.__class__.__name__, self.file_id)

    def transform(self):
        self.file_path = os.path.join(
            tempfile.mkdtemp(), '{}'.format(self.file_id))

        self.gc.downloadFile(self.file_id, self.file_path)

        return self.file_path

    def cleanup(self):
        shutil.rmtree(os.path.dirname(self.file_path),
                      ignore_errors=True)


class GirderItemMetadata(GirderClientTransform):
    def __init__(self, _id, **kwargs):
        super(GirderItemMetadata, self).__init__(**kwargs)
        self.item_id = _id

    def _repr_model_(self):
        return "{}('{}')".format(self.__class__.__name__, self.item_id)

    def transform(self, data):
        self.gc.addMetadataToItem(self.item_id, data)

        return data


class GirderUploadToItem(GirderClientResultTransform):
    def __init__(self, _id, delete_file=False, upload_kwargs=None, **kwargs):
        super(GirderUploadToItem, self).__init__(**kwargs)
        self.item_id = _id
        self.upload_kwargs = upload_kwargs or {}
        self.delete_file = delete_file

    def _repr_model_(self):
        return "{}('{}')".format(self.__class__.__name__, self.item_id)

    def transform(self, path):
        self.output_file_path = path
        if os.path.isdir(path):
            for f in os.listdir(path):
                f = os.path.join(path, f)
                if os.path.isfile(f):
                    self.gc.uploadFileToItem(self.item_id, f, **self.upload_kwargs)
        else:
            self.gc.uploadFileToItem(self.item_id, path, **self.upload_kwargs)
        return self.item_id

    def cleanup(self):
        if self.delete_file is True:
            if os.path.isdir(self.output_file_path):
                shutil.rmtree(self.output_file_path)
            else:
                os.remove(self.output_file_path)


class GirderUploadToFolder(GirderClientResultTransform):
    def __init__(self, _id, delete_file=False, upload_kwargs=None, **kwargs):
        super(GirderUploadToFolder, self).__init__(**kwargs)
        self.folder_id = _id
        self.upload_kwargs = upload_kwargs or {}
        self.delete_file = delete_file

    def _repr_model_(self):
        return "{}('{}')".format(self.__class__.__name__, self.folder_id)

    def transform(self, path):
        self.output_file_path = path
        if os.path.isdir(path):
            for f in os.listdir(path):
                f = os.path.join(path, f)
                if os.path.isfile(f):
                    self.gc.uploadFileToFolder(self.folder_id, f, **self.upload_kwargs)
        else:
            self.gc.uploadFileToFolder(self.folder_id, path, **self.upload_kwargs)
        return self.folder_id

    def cleanup(self):
        if self.delete_file is True:
            if os.path.isdir(self.output_file_path):
                shutil.rmtree(self.output_file_path)
            else:
                os.remove(self.output_file_path)
