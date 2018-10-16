import mimetypes
import os
import shutil
import tempfile

from girder_client import GirderClient
from six.moves.urllib.parse import urlencode

from ..transform import ResultTransform, Transform


class GirderClientTransform(Transform):
    def __init__(self, *args, **kwargs):
        gc = kwargs.pop('gc', None)

        try:
            if gc is None:
                # We need to resolve Girder's API URL, but girder_worker can
                # specify a different value than what Girder gets from a rest
                # request.
                # Girder 3
                try:
                    from girder_worker.girder_plugin.utils import getWorkerApiUrl
                except ImportError:
                    # Girder 2
                    try:
                        from girder.plugins.worker.utils import getWorkerApiUrl
                    # Fall back if the worker plugin is unavailble
                    except ImportError:
                        from girder.api.rest import getApiUrl as getWorkerApiUrl
                from girder.api.rest import getCurrentToken
                self.gc = GirderClient(apiUrl=getWorkerApiUrl())
                self.gc.token = getCurrentToken()['_id']
            else:
                self.gc = gc
        except ImportError:
            self.gc = None


class GirderClientResultTransform(ResultTransform, GirderClientTransform):
    pass


class GirderFileId(GirderClientTransform):
    """
    This transform downloads a Girder File to the local machine and passes its
    local path into the function.

    :param _id: The ID of the file to download.
    :type _id: str
    """
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
    """
    This is a result hook transform that uploads a file or flat directory of files
    to an item in Girder.

    :param _id: The ID of the item to upload into.
    :type _id: str
    :param delete_file: Whether to delete the local data afterward
    :type delete_file: bool
    :param upload_kwargs: Additional kwargs to pass to the upload method.
    :type upload_kwargs: dict
    """
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
    """
    This is a result hook transform that uploads a file or directory recursively
    to a folder in Girder.

    :param _id: The ID of the folder to upload into.
    :type _id: str
    :param delete_file: Whether to delete the local data afterward
    :type delete_file: bool
    :param upload_kwargs: Additional kwargs to pass to the upload method.
    :type upload_kwargs: dict
    """
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


class GirderUploadJobArtifact(GirderClientResultTransform):
    """
    This class can be used to upload a directory of files or a single file
    as artifacts attached to a Girder job. These files are only uploaded
    if they exist, so this is an optional output.

    Currently, only a flat directory of files is supported; the transform does not
    recurse through nested directories, though that may change in the future.

    :param job_id: The ID of the job to attach the file(s) to.
    :type job_id: str or ObjectId
    :param name: Name for the artifact (only if it's a single file).
    :type name: str
    """
    def __init__(self, job_id=None, name=None, **kwargs):
        super(GirderUploadJobArtifact, self).__init__(**kwargs)
        self.job_id = job_id
        self.name = name

    def _repr_model_(self):
        return "{}('{}')".format(self.__class__.__name__, self.job_id)

    def _upload_artifact(self, file, name=None):
        qs = urlencode({
            'name': name or os.path.basename(file),
            'size': os.stat(file).st_size,
            'mimeType': mimetypes.guess_type(file)[0]
        })
        with open(file, 'rb') as fh:
            self.gc.post('job/%s/artifact?%s' % (self.job_id, qs), data=fh)

    def transform(self, path):
        if self.job_id is None:
            self.job_id = str(self.job['_id'])

        if os.path.isdir(path):
            for f in os.listdir(path):
                f = os.path.join(path, f)
                if os.path.isfile(f):
                    self._upload_artifact(f)
        elif os.path.isfile(path):
            self._upload_artifact(path, self.name)
