import json as python_json

import mock
import pytest

from girder_worker_utils import json


def test_json_decoder_class_interface():
    decoder = json.JSONDecoder()
    assert isinstance(decoder, python_json.JSONDecoder)


def test_json_encoder_class_interface():
    encoder = json.JSONEncoder()
    assert isinstance(encoder, python_json.JSONEncoder)


@mock.patch.object(json.json, 'load', return_value='return')
def test_load_calls_json_load(load):
    def object_hook(data):
        return data

    rval = json.load('filename.json', object_hook=object_hook)
    assert rval == 'return'
    load.assert_called_once_with('filename.json', object_hook=object_hook)


@mock.patch.object(json.json, 'loads', return_value='return')
def test_loads_calls_json_loads(loads):
    def object_hook(data):
        return data

    rval = json.loads('{}', object_hook=object_hook)
    assert rval == 'return'
    loads.assert_called_once_with('{}', object_hook=object_hook)


@mock.patch.object(json.json, 'dump', return_value='return')
def test_dump_calls_json_dump(dump):
    obj = {}
    rval = json.dump(obj, fp='file', cls=python_json.JSONEncoder)
    assert rval == 'return'
    dump.assert_called_once_with(obj, fp='file', cls=python_json.JSONEncoder)


@mock.patch.object(json.json, 'dumps', return_value='return')
def test_dumps_calls_json_dumps(dumps):
    obj = {}
    rval = json.dumps(obj, cls=python_json.JSONEncoder)
    assert rval == 'return'
    dumps.assert_called_once_with(obj, cls=python_json.JSONEncoder)


def test_dumps_raises_on_unhandled_type():
    class CustomClass(object):
        pass

    obj = CustomClass()
    with pytest.raises(TypeError):
        json.dumps(obj)


def test_register_object_hook_function():
    hook_name = 'girder_worker_utils.test.bare_function_hook'
    func = mock.Mock(return_value='return')
    args = ('a', 'b')
    kwargs = {'c': 'c'}
    json.register_hook(hook_name, func, *args, **kwargs)

    data = {'__json_hook__': hook_name}
    rval = json.object_hook(data)

    assert rval == 'return'
    func.assert_called_once_with(*(args + (data,)), **kwargs)


def test_register_object_hook_decorator():
    hook_name = 'girder_worker_utils.test.decorated_hook'
    func = mock.Mock(return_value='return')

    @json.hook(hook_name)
    def decorated_hook(*args, **kwargs):
        return func(*args, **kwargs)

    data = {'__json_hook__': hook_name}
    rval = json.object_hook(data)

    assert rval == 'return'
    func.assert_called_once_with(data)


def test_encode_decode_class():
    hook_name = 'girder_worker_utils.test.decode_with_hook'
    deserialized = {}

    class TestClass(object):
        def __json__(self):
            return {'__json_hook__': hook_name}

        @staticmethod
        @json.hook(hook_name)
        def deserialize(data):
            return deserialized

    data = {'test instance': TestClass()}
    rval = json.loads(json.dumps(data))
    assert rval['test instance'] is deserialized
