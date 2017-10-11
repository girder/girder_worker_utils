from girder_worker_utils.transform import Transform


def test_default_transform_behavior():
    assert Transform().transform() is None


def test_noop_transform():
    assert Transform('some value').transform() == 'some value'


def test_transform_serialize():
    args = ('arg1', 'arg2', 'arg3')
    kwargs = {'kwarg1': 'kwarg1', 'kwarg2': 'kwarg2'}
    t = Transform(*args, **kwargs)
    assert t.serialize() == {
        '__state__': {
            'args': args,
            'kwargs': kwargs
        },
        '_class': 'Transform',
        '_module': 'girder_worker_utils.transform'
    }


def test_transform_json():
    args = ('arg1', 'arg2', 'arg3')
    kwargs = {'kwarg1': 'kwarg1', 'kwarg2': 'kwarg2'}
    t = Transform(*args, **kwargs)
    assert t.__json__() == t.serialize()


def test_deserialize():
    t = Transform.deserialize({
        'args': ('a', 'b'),
        'kwargs': {'c': 'c', 'd': 'd'}
    })
    assert t.__state__['args'] == ('a', 'b')
    assert t.__state__['kwargs'] == {'c': 'c', 'd': 'd'}
