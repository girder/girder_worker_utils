from girder_worker_utils import json
from girder_worker_utils.transform import Transform


def test_default_transform_behavior():
    assert Transform().transform() is None


def test_noop_transform():
    assert Transform('some value').transform() == 'some value'


def test_transform_serialize_roundtrip():
    args = ('arg1', 'arg2', 'arg3')
    kwargs = {'kwarg1': 'kwarg1', 'kwarg2': 'kwarg2'}
    original_instance = Transform(*args, **kwargs)
    new_instance = json.loads(json.dumps(original_instance))

    assert isinstance(new_instance, Transform)
    assert new_instance.__state__ == {'args': args, 'kwargs': kwargs}
