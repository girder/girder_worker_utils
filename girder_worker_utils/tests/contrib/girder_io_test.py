import os
import sys
import types

import girder_client
import mock
import pytest

from girder_worker_utils.transforms.contrib import girder_io


@pytest.fixture
def mock_file_model():
    girder = types.ModuleType('girder')
    girder.models = types.ModuleType('models')
    girder.models.file = types.ModuleType('file')
    sys.modules['girder'] = girder
    sys.modules['girder.models'] = girder.models
    sys.modules['girder.models.file'] = girder.models.file
    girder.exceptions = types.ModuleType('exceptions')
    sys.modules['girder.exceptions'] = girder.exceptions

    def fileObject():
        pass

    girder.models.file.File = lambda: fileObject
    return girder.models.file.File()


@pytest.fixture
def mock_file_load(mock_file_model):
    from girder.models.file import File

    def load(*args, **kwargs):
        return {'name': 'the_name'}

    File().load = load
    return File()


@pytest.fixture
def mock_file_getLocalFilePath(mock_file_model):
    import girder.exceptions
    from girder.models.file import File

    girder.exceptions.FilePathException = Exception

    def getLocalFilePath(*args, **kwargs):
        return os.path.realpath(__file__)

    File().getLocalFilePath = getLocalFilePath


@pytest.fixture
def mock_gc():
    return mock.MagicMock(spec=girder_client.GirderClient)


@pytest.fixture
def mock_rmtree():
    with mock.patch('shutil.rmtree') as rmtree:
        yield rmtree


def test_GirderFileIdAllowDirect_without_env(
        mock_gc, mock_rmtree, mock_file_load, mock_file_getLocalFilePath):
    t = girder_io.GirderFileIdAllowDirect(_id='the_id', gc=mock_gc)
    t.transform()
    mock_gc.downloadFile.assert_called_once()
    assert 'the_id' in mock_gc.downloadFile.call_args[0]
    mock_rmtree.assert_not_called()
    t.cleanup()
    mock_rmtree.assert_called_once()


@mock.patch.dict(os.environ, {'GW_DIRECT_PATHS': 'true'})
def test_GirderFileIdAllowDirect_with_env(
        mock_gc, mock_rmtree, mock_file_load, mock_file_getLocalFilePath):
    t = girder_io.GirderFileIdAllowDirect(_id='the_id', gc=mock_gc)
    t.transform()
    mock_gc.downloadFile.assert_not_called()
    t.cleanup()
    mock_rmtree.assert_not_called()
