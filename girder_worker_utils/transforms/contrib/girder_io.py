import os
import shutil
import tempfile

from ..girder_io import GirderClientTransform


class GirderFileIdAllowDirect(GirderClientTransform):
    """
    This transform either uses direct path to access a file, if possible and
    allowed, or downloads a Girder File to the local machine and passes its
    local path into the function.

    WARNING: if a direct path is used, the task MUST NOT modify the file.  It
    is the resposibility of the user of this transform to ensure tasks treat
    files as read-only.

    :param _id: The ID of the file to download.
    :type _id: str
    """
    def __init__(self, _id, **kwargs):
        super(GirderFileIdAllowDirect, self).__init__(**kwargs)
        from girder.models.file import File
        from girder.exceptions import FilePathException
        self.file_id = _id
        file = File().load(self.file_id, force=True)
        # Store the original file name so that, if downloading the file, the
        # extension can be preserved.
        self.file_name = file['name']
        try:
            # Add a local file path if direct paths are allowed
            self.local_file_path = File().getLocalFilePath(file)
        except FilePathException:
            self.local_file_path = None

    def _repr_model_(self):
        if self.local_file_path:
            return '{}({!r}) - {!r} - {!r}'.format(
                self.__class__.__name__, self.file_id, self.file_name, self.local_file_path)
        return '{}({!r}) - {!r}'.format(self.__class__.__name__, self.file_id, self.file_name)

    def _allowDirectPath(self):
        """
        Check if the worker environment permits direct paths.  This just checks
        if the environment variable GW_DIRECT_PATHS is set to a non-empry
        value.
        """
        if os.environ.get('GW_DIRECT_PATHS'):
            return True
        return False

    def transform(self):
        # Don't download if self.local_file_path is set and direct paths are
        # allowed.
        if (self.local_file_path and self._allowDirectPath() and
                os.path.isfile(self.local_file_path)):
            self.temp_dir_path = None
            self.file_path = self.local_file_path
        else:
            self.temp_dir_path = tempfile.mkdtemp()
            self.file_path = os.path.join(self.temp_dir_path, '{}{}'.format(
                self.file_id, os.path.splitext(self.file_name)[1]))
            self.gc.downloadFile(self.file_id, self.file_path)
        return self.file_path

    def cleanup(self):
        if self.temp_dir_path:
            shutil.rmtree(self.temp_dir_path, ignore_errors=True)
