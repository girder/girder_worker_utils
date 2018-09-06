import pytest
import six
from girder_worker_utils.decorators import (
    GWArgSpec,
    Varargs,
    Kwargs,
    PosArg,
    KWArg)

def arg_varargs_kwarg(a, *args, b='test'): pass
def arg_varargs_kwarg_no_default(a, *args, b): pass
def arg_emptyvarargs_kwarg(a, *, b='test'): pass
def arg_emptyvarargs_kwarg_no_default(a, *, b): pass

def arg_with_annotation(a: int): pass


@pytest.mark.parametrize('func,classes', [
    (arg_varargs_kwarg, [PosArg, Varargs, KWArg]),
    (arg_varargs_kwarg_no_default, [PosArg, Varargs, KWArg]),
    (arg_emptyvarargs_kwarg, [PosArg, KWArg]),
    (arg_emptyvarargs_kwarg_no_default, [PosArg, KWArg])
])
def test_GWArgSpec_arguments_returns_expected_classes(func, classes):
    spec = GWArgSpec(func)
    assert len(spec.arguments) == len(classes)
    for arg, cls in zip(spec.arguments, classes):
        assert isinstance(arg, cls)


no_varargs = [arg_emptyvarargs_kwarg,
              arg_emptyvarargs_kwarg_no_default]


@pytest.mark.parametrize('func', no_varargs)
def test_GWArgSpec_varargs_returns_None(func):
    spec = GWArgSpec(func)
    assert spec.varargs is None


with_varargs = [
    arg_varargs_kwarg,
    arg_varargs_kwarg_no_default]


@pytest.mark.parametrize('func', with_varargs)
def test_GWArgSpec_varargs_returns_Vararg(func):
    spec = GWArgSpec(func)
    assert isinstance(spec.varargs, Varargs)


@pytest.mark.parametrize('func,names', [
    (arg_varargs_kwarg, ["a"]),
    (arg_varargs_kwarg_no_default, ["a"]),
    (arg_emptyvarargs_kwarg, ["a"]),
    (arg_emptyvarargs_kwarg_no_default, ["a"]),
])
def test_GWArgSpec_positional_args_correct_names(func, names):
    spec = GWArgSpec(func)
    assert len(spec.positional_args) == len(names)
    for p, n in zip(spec.positional_args, names):
        assert isinstance(p, PosArg)
        assert p.name == n


# TODO positional_args returns None test

@pytest.mark.parametrize('func,names', [
    (arg_varargs_kwarg, ['b']),
    (arg_varargs_kwarg_no_default, ['b']),
    (arg_emptyvarargs_kwarg, ['b']),
    (arg_emptyvarargs_kwarg_no_default, ['b'])
])
def test_GWArgSpec_keyword_args_correct_names(func, names):
    spec = GWArgSpec(func)
    assert len(spec.keyword_args) == len(names)
    for p, n in zip(spec.keyword_args, names):
        assert isinstance(p, KWArg)
        assert p.name == n

# TODO keyword_args returns None test

@pytest.mark.parametrize('func,defaults', [
    (arg_varargs_kwarg, ['test']),
    (arg_emptyvarargs_kwarg, ['test'])
])
def test_GWArgSpec_keyword_args_have_defaults(func, defaults):
    spec = GWArgSpec(func)
    assert len(spec.keyword_args) == len(defaults)
    for p, d in zip(spec.keyword_args, defaults):
        assert hasattr(p, 'default')
        assert p.default == d

@pytest.mark.parametrize('func', [
    arg_varargs_kwarg_no_default,
    arg_emptyvarargs_kwarg_no_default
])
def test_GWArgSpec_keyword_args_with_no_defaults_have_no_defaults(func):
    spec = GWArgSpec(func)
    for p in spec.keyword_args:
        assert not hasattr(p, "default")


@pytest.mark.parametrize('func,data_types', [
    (arg_with_annotation, [int])
])
def test_GWArgSpec_positional_args_with_annotation_have_data_type(func, data_types):
    spec = GWArgSpec(func)
    assert len(spec.positional_args) == len(data_types)
    for p, d in zip(spec.positional_args, data_types):
        assert hasattr(p, "data_type")
        assert p.data_type == d
