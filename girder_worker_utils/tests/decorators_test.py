import pytest

from girder_worker_utils import types
from girder_worker_utils.decorators import task, task_input, task_output


@task()
@task_input('-n', type=types.Integer(), help='The element to return')
@task_output('value', type=types.Integer())
def fibonacci(n):
    """Compute a fibonacci number."""
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


@task()
@task_input('--val', help='The value to return')
@task_output('noop_value')
def keyword_func(val='test'):
    """Return a value."""
    return val


@task()
@task_input('--arg1')
@task_input('--arg2', type=types.Choice(('a', 'b')))
@task_input('--kwarg1', nargs=2)
@task_input('--kwarg2', type=types.Integer(min=0, max=10))
@task_input('--kwarg3', type=types.Choice((1, 2, 3, 4, 5)), multiple=True)
def complex_func(arg1, arg2, kwarg1=('one', 'two'), kwarg2=4, kwarg3=(1, 2)):
    return {
        'arg1': arg1,
        'arg2': arg2,
        'kwarg1': kwarg1,
        'kwarg2': kwarg2,
        'kwarg3': kwarg3
    }


def test_positional_argument():
    desc = fibonacci.describe()
    assert len(desc['inputs']) == 1
    assert desc['name'].split('.')[-1] == 'fibonacci'
    assert desc['description'] == \
        'Compute a fibonacci number.'

    assert desc['inputs'][0]['name'] == 'n'
    assert desc['inputs'][0]['description'] == \
        'The element to return'

    assert fibonacci.call_item_task({'n': {'data': 10}}) == 55
    with pytest.raises(TypeError):
        fibonacci.call_item_task({})


def test_keyword_argument():
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


def test_multiple_arguments():
    desc = complex_func.describe()
    assert len(desc['inputs']) == 5
    assert desc['name'].split('.')[-1] == 'complex_func'

    assert desc['inputs'][0]['name'] == 'arg1'
    assert desc['inputs'][1]['name'] == 'arg2'
    assert desc['inputs'][2]['name'] == 'kwarg1'
    assert desc['inputs'][3]['name'] == 'kwarg2'
    assert desc['inputs'][4]['name'] == 'kwarg3'

    with pytest.raises(TypeError):
        complex_func.call_item_task({})

    with pytest.raises(TypeError):
        complex_func.call_item_task({
            'arg1': {'data': 'value'}
        })

    assert complex_func.call_item_task({
        'arg1': {'data': 'value'},
        'arg2': {'data': 'a'}
    }) == {
        'arg1': 'value',
        'arg2': 'a',
        'kwarg1': ('one', 'two'),
        'kwarg2': 4,
        'kwarg3': (1, 2)
    }

    assert complex_func.call_item_task({
        'arg1': {'data': 'value'},
        'arg2': {'data': 'b'},
        'kwarg1': {'data': ['one', 'two']},
        'kwarg2': {'data': 10},
        'kwarg3': {'data': (1, 4)}
    }) == {
        'arg1': 'value',
        'arg2': 'b',
        'kwarg1': ['one', 'two'],
        'kwarg2': 10,
        'kwarg3': (1, 4)
    }
