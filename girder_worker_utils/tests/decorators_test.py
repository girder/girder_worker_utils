import deprecation
import pytest

from girder_worker_utils import decorators
from girder_worker_utils import types
from girder_worker_utils.decorators import (
    argument,
    GWFuncDesc,
    KeywordArg,
    KwargsArg,
    parameter,
    PositionalArg,
    VarsArg)


@deprecation.fail_if_not_removed
def test_positional_argument():

    @argument('n', types.Integer, help='The element to return')
    def fibonacci(n):
        """Compute a fibonacci number."""
        if n <= 2:
            return 1
        return fibonacci(n - 1) + fibonacci(n - 2)

    desc = fibonacci.describe()
    assert len(desc['inputs']) == 1
    assert desc['name'].split('.')[-1] == 'fibonacci'
    assert desc['description'] == \
        'Compute a fibonacci number.'

    assert desc['inputs'][0]['name'] == 'n'
    assert desc['inputs'][0]['description'] == \
        'The element to return'

    assert fibonacci.call_item_task({'n': {'data': 10}}) == 55
    with pytest.raises(decorators.MissingInputException):
        fibonacci.call_item_task({})


@deprecation.fail_if_not_removed
def test_keyword_argument():

    @argument('val', types.String, help='The value to return')
    def keyword_func(val='test'):
        """Return a value."""
        return val

    desc = keyword_func.describe()
    assert len(desc['inputs']) == 1
    assert desc['name'].split('.')[-1] == 'keyword_func'
    assert desc['description'] == \
        'Return a value.'

    assert desc['inputs'][0]['name'] == 'val'
    assert desc['inputs'][0]['description'] == \
        'The value to return'

    assert keyword_func.call_item_task({'val': {'data': 'foo'}}) == 'foo'
    assert keyword_func.call_item_task({}) == 'test'


@deprecation.fail_if_not_removed
def test_multiple_arguments():

    @argument('arg1', types.String)
    @argument('arg2', types.StringChoice, choices=('a', 'b'))
    @argument('kwarg1', types.StringVector)
    @argument('kwarg2', types.Number, min=0, max=10)
    @argument('kwarg3', types.NumberMultichoice, choices=(1, 2, 3, 4, 5))
    def complex_func(arg1, arg2, kwarg1=('one',), kwarg2=4, kwarg3=(1, 2)):
        return {
            'arg1': arg1,
            'arg2': arg2,
            'kwarg1': kwarg1,
            'kwarg2': kwarg2,
            'kwarg3': kwarg3
        }

    desc = complex_func.describe()
    assert len(desc['inputs']) == 5
    assert desc['name'].split('.')[-1] == 'complex_func'

    assert desc['inputs'][0]['name'] == 'arg1'
    assert desc['inputs'][1]['name'] == 'arg2'
    assert desc['inputs'][2]['name'] == 'kwarg1'
    assert desc['inputs'][3]['name'] == 'kwarg2'
    assert desc['inputs'][4]['name'] == 'kwarg3'

    with pytest.raises(decorators.MissingInputException):
        complex_func.call_item_task({})

    with pytest.raises(decorators.MissingInputException):
        complex_func.call_item_task({
            'arg1': {'data': 'value'}
        })

    with pytest.raises(ValueError):
        complex_func.call_item_task({
            'arg1': {'data': 'value'},
            'arg2': {'data': 'invalid'}
        })

    with pytest.raises(TypeError):
        complex_func.call_item_task({
            'arg1': {'data': 'value'},
            'arg2': {'data': 'a'},
            'kwarg2': {'data': 'foo'}
        })

    assert complex_func.call_item_task({
        'arg1': {'data': 'value'},
        'arg2': {'data': 'a'}
    }) == {
        'arg1': 'value',
        'arg2': 'a',
        'kwarg1': ('one',),
        'kwarg2': 4,
        'kwarg3': (1, 2)
    }

    assert complex_func.call_item_task({
        'arg1': {'data': 'value'},
        'arg2': {'data': 'b'},
        'kwarg1': {'data': 'one,two'},
        'kwarg2': {'data': 10},
        'kwarg3': {'data': (1, 4)}
    }) == {
        'arg1': 'value',
        'arg2': 'b',
        'kwarg1': ['one', 'two'],
        'kwarg2': 10,
        'kwarg3': (1, 4)
    }


@deprecation.fail_if_not_removed
def test_girder_input_mode():

    @argument('item', types.GirderItem)
    @argument('folder', types.GirderFolder)
    def girder_types_func(item, folder):
        return item, folder

    item, folder = girder_types_func.call_item_task({
        'item': {
            'mode': 'girder',
            'id': 'itemid',
            'resource_type': 'item',
            'fileName': 'file.txt'
        },
        'folder': {
            'mode': 'girder',
            'id': 'folderid',
            'resource_type': 'folder'
        }
    })

    assert item == 'itemid'
    assert folder == 'folderid'


@deprecation.fail_if_not_removed
def test_missing_description_exception():
    def func():
        pass

    with pytest.raises(decorators.MissingDescriptionException):
        decorators.get_description_attribute(func)


@deprecation.fail_if_not_removed
def test_argument_name_not_string():
    with pytest.raises(TypeError):
        argument(0, types.Integer)


@deprecation.fail_if_not_removed
def test_argument_name_not_a_parameter():
    with pytest.raises(ValueError):
        @argument('notarg', types.Integer)
        def func(arg):
            pass


@deprecation.fail_if_not_removed
def test_unhandled_input_binding():
    arg = argument('arg', types.Integer)
    with pytest.raises(ValueError):
        decorators.get_input_data(arg, {})

###########################

def arg(a): pass # noqa
def varargs(*args): pass # noqa
def kwarg(a='test'): pass # noqa
def kwargs(**kwargs): pass # noqa
def arg_arg(a, b): pass # noqa
def arg_varargs(a, *args): pass # noqa
def arg_kwarg(a, b='test'): pass # noqa
def arg_kwargs(a, **kwargs): pass # noqa
def kwarg_varargs(a='test', *args): pass # noqa
def kwarg_kwarg(a='testa', b='testb'): pass # noqa
def kwarg_kwargs(a='test', **kwargs): pass # noqa
def arg_kwarg_varargs(a, b='test', *args): pass # noqa
def arg_kwarg_kwargs(a, b='test', **kwargs): pass # noqa
def arg_kwarg_varargs_kwargs(a, b='test', *args, **kwargs): pass # noqa


@pytest.mark.parametrize('func,classes', [
    (arg, [PositionalArg]),
    (varargs, [VarsArg]),
    (kwarg, [KeywordArg]),
    (kwargs, [KwargsArg]),
    (arg_arg, [PositionalArg, PositionalArg]),
    (arg_varargs, [PositionalArg, VarsArg]),
    (arg_kwarg, [PositionalArg, KeywordArg]),
    (arg_kwargs, [PositionalArg, KwargsArg]),
    (kwarg_varargs, [KeywordArg, VarsArg]),
    (kwarg_kwarg, [KeywordArg, KeywordArg]),
    (kwarg_kwargs, [KeywordArg, KwargsArg]),
    (arg_kwarg_varargs, [PositionalArg, KeywordArg, VarsArg]),
    (arg_kwarg_kwargs, [PositionalArg, KeywordArg, KwargsArg]),
    (arg_kwarg_varargs_kwargs, [PositionalArg, KeywordArg, VarsArg, KwargsArg])
])
def test_GWFuncDesc_arguments_returns_expected_classes(func, classes):
    spec = GWFuncDesc(func)
    assert len(spec.arguments) == len(classes)
    for arg, cls in zip(spec.arguments, classes):
        assert isinstance(arg, cls)


no_varargs = [arg, kwarg, kwargs, arg_arg, arg_kwarg,
              arg_kwargs, kwarg_kwarg, kwarg_kwargs,
              arg_kwarg_kwargs]


@pytest.mark.parametrize('func', no_varargs)
def test_GWFuncDesc_varargs_returns_None(func):
    spec = GWFuncDesc(func)
    assert spec.varargs is None


with_varargs = [varargs, arg_varargs, kwarg_varargs,
                arg_kwarg_varargs, arg_kwarg_varargs_kwargs]


@pytest.mark.parametrize('func', with_varargs)
def test_GWFuncDesc_varargs_returns_Vararg(func):
    spec = GWFuncDesc(func)
    assert isinstance(spec.varargs, VarsArg)


@pytest.mark.parametrize('func,names', [
    (arg, ["a"]),
    (arg_arg, ["a", "b"]),
    (arg_varargs, ["a"]),
    (arg_kwarg, ["a"]),
    (arg_kwargs, ["a"]),
    (arg_kwarg_kwargs, ["a"]),
    (arg_kwarg_varargs_kwargs, ["a"])
])
def test_GWFuncDesc_positional_args_correct_names(func, names):
    spec = GWFuncDesc(func)
    assert len(spec.positional_args) == len(names)
    for p, n in zip(spec.positional_args, names):
        assert isinstance(p, PositionalArg)
        assert p.name == n


@pytest.mark.parametrize('func', [
    varargs, kwarg, kwargs, kwarg_varargs,
    kwarg_kwarg, kwarg_kwargs
])
def test_GWFuncDesc_positional_args_returns_empty_list_if_no_positional_args(func):
    spec = GWFuncDesc(func)
    assert len(spec.positional_args) == 0


@pytest.mark.parametrize('func,names', [
    (kwarg, ['a']),
    (arg_kwarg, ['b']),
    (kwarg_varargs, ['a']),
    (kwarg_kwarg, ['a', 'b']),
    (kwarg_kwargs, ['a']),
    (arg_kwarg_varargs, ['b']),
    (arg_kwarg_kwargs, ['b']),
    (arg_kwarg_varargs_kwargs, ['b']),
])
def test_GWFuncDesc_keyword_args_correct_names(func, names):
    spec = GWFuncDesc(func)
    assert len(spec.keyword_args) == len(names)
    for p, n in zip(spec.keyword_args, names):
        assert isinstance(p, KeywordArg)
        assert p.name == n


@pytest.mark.parametrize('func', [
    arg, varargs, kwargs, arg_arg, arg_varargs, arg_kwargs
])
def test_GWFuncDesc_keyword_args_returns_empty_list_if_no_keyword_args(func):
    spec = GWFuncDesc(func)
    assert len(spec.keyword_args) == 0


@pytest.mark.parametrize('func,defaults', [
    (kwarg, ['test']),
    (arg_kwarg, ['test']),
    (kwarg_varargs, ['test']),
    (kwarg_kwarg, ['testa', 'testb']),
    (kwarg_kwargs, ['test']),
    (arg_kwarg_varargs, ['test']),
    (arg_kwarg_kwargs, ['test']),
    (arg_kwarg_varargs_kwargs, ['test']),
])
def test_GWFuncDesc_keyword_args_have_defaults(func, defaults):
    spec = GWFuncDesc(func)
    assert len(spec.keyword_args) == len(defaults)
    for p, d in zip(spec.keyword_args, defaults):
        assert hasattr(p, 'default')
        assert p.default == d


def test_parameter_decorator_adds_metadata():
    @parameter('a', test='TEST')
    def arg(a):
        pass

    desc = GWFuncDesc.get_description(arg)

    assert hasattr(desc.arguments[0], 'test')
    assert desc.arguments[0].test == 'TEST'


# TODO more tests around other argument types (e.g. kwargs varargs etc)
