import pytest

from girder_worker_utils.decorators import (
    GWFuncDesc,
    Varargs,
    Arg,
    KWArg)


def arg_varargs_kwarg(a, *args, b='test'): pass  # noqa
def arg_varargs_kwarg_no_default(a, *args, b): pass # noqa
def arg_emptyvarargs_kwarg(a, *, b='test'): pass # noqa
def arg_emptyvarargs_kwarg_no_default(a, *, b): pass # noqa
def arg_with_annotation(a: int): pass # noqa


@pytest.mark.parametrize('func,classes', [
    (arg_varargs_kwarg, [Arg, Varargs, KWArg]),
    (arg_varargs_kwarg_no_default, [Arg, Varargs, KWArg]),
    (arg_emptyvarargs_kwarg, [Arg, KWArg]),
    (arg_emptyvarargs_kwarg_no_default, [Arg, KWArg])
])
def test_GWFuncDesc_arguments_returns_expected_classes(func, classes):
    spec = GWFuncDesc(func)
    assert len(spec.arguments) == len(classes)
    for arg, cls in zip(spec.arguments, classes):
        assert isinstance(arg, cls)


no_varargs = [arg_emptyvarargs_kwarg,
              arg_emptyvarargs_kwarg_no_default]


@pytest.mark.parametrize('func', no_varargs)
def test_GWFuncDesc_varargs_returns_None(func):
    spec = GWFuncDesc(func)
    assert spec.varargs is None


with_varargs = [
    arg_varargs_kwarg,
    arg_varargs_kwarg_no_default]


@pytest.mark.parametrize('func', with_varargs)
def test_GWFuncDesc_varargs_returns_Vararg(func):
    spec = GWFuncDesc(func)
    assert isinstance(spec.varargs, Varargs)


@pytest.mark.parametrize('func,names', [
    (arg_varargs_kwarg, ["a"]),
    (arg_varargs_kwarg_no_default, ["a"]),
    (arg_emptyvarargs_kwarg, ["a"]),
    (arg_emptyvarargs_kwarg_no_default, ["a"]),
])
def test_GWFuncDesc_positional_args_correct_names(func, names):
    spec = GWFuncDesc(func)
    assert len(spec.positional_args) == len(names)
    for p, n in zip(spec.positional_args, names):
        assert isinstance(p, Arg)
        assert p.name == n


@pytest.mark.parametrize('func,names', [
    (arg_varargs_kwarg, ['b']),
    (arg_varargs_kwarg_no_default, ['b']),
    (arg_emptyvarargs_kwarg, ['b']),
    (arg_emptyvarargs_kwarg_no_default, ['b'])
])
def test_GWFuncDesc_keyword_args_correct_names(func, names):
    spec = GWFuncDesc(func)
    assert len(spec.keyword_args) == len(names)
    for p, n in zip(spec.keyword_args, names):
        assert isinstance(p, KWArg)
        assert p.name == n


@pytest.mark.parametrize('func,defaults', [
    (arg_varargs_kwarg, ['test']),
    (arg_emptyvarargs_kwarg, ['test'])
])
def test_GWFuncDesc_keyword_args_have_defaults(func, defaults):
    spec = GWFuncDesc(func)
    assert len(spec.keyword_args) == len(defaults)
    for p, d in zip(spec.keyword_args, defaults):
        assert hasattr(p, 'default')
        assert p.default == d


@pytest.mark.parametrize('func', [
    arg_varargs_kwarg_no_default,
    arg_emptyvarargs_kwarg_no_default
])
def test_GWFuncDesc_keyword_args_with_no_defaults_have_no_defaults(func):
    spec = GWFuncDesc(func)
    for p in spec.keyword_args:
        assert not hasattr(p, "default")


@pytest.mark.parametrize('func,data_types', [
    (arg_with_annotation, [int])
])
def test_GWFuncDesc_positional_args_with_annotation_have_data_type(func, data_types):
    spec = GWFuncDesc(func)
    assert len(spec.positional_args) == len(data_types)
    for p, d in zip(spec.positional_args, data_types):
        assert hasattr(p, "data_type")
        assert p.data_type == d
