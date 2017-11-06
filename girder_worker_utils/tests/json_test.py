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



def deserialize_function(data):
    return data

def test_class_hint_object_hook_function():
    data = {
        'key': 'value',
        '__class_hint__': {
            'func': 'deserialize_function',
            'module': 'girder_worker_utils.tests.json_test'
    }}
    rval = json.object_hook(data)
    assert rval == {'key': 'value'}


class ObjectHookClass(object):
    def __init__(self, data):
        self.data = data

def test_class_hint_object_hook_class():
    data = {
        'key': 'value',
        '__class_hint__': {
            'func': 'ObjectHookClass',
            'module': 'girder_worker_utils.tests.json_test'
    }}
    rval = json.object_hook(data)
    assert isinstance(rval, ObjectHookClass)
    assert rval.data == {'key': 'value'}



class ClassMethodObjectHookClass(object):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def deserialize_class(cls, data):
        return data

    @staticmethod
    def deserialize_static(data):
        return data

def test_class_hint_object_hook_classmethod():
    data = {
        'key': 'value',
        '__class_hint__': {
            'cls': 'ClassMethodObjectHookClass',
            'func': 'deserialize_class',
            'module': 'girder_worker_utils.tests.json_test'
    }}
    rval = json.object_hook(data)
    assert rval == {'key': 'value'}


def test_class_hint_object_hook_staticmethod():
    data = {
        'key': 'value',
        '__class_hint__': {
            'cls': 'ClassMethodObjectHookClass',
            'func': 'deserialize_static',
            'module': 'girder_worker_utils.tests.json_test'
    }}
    rval = json.object_hook(data)
    assert rval == {'key': 'value'}
