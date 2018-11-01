from inspect import getdoc

import deprecation

from girder_worker_utils import __version__

try:
    from inspect import signature, Parameter
except ImportError:  # pragma: nocover
    from funcsigs import signature, Parameter

import six


class MissingDescriptionException(Exception):
    """Raised when a function is missing description decorators."""


class MissingInputException(Exception):
    """Raised when a required input is missing."""


def get_description_attribute(func):
    """Get the private description attribute from a function."""
    # func = getattr(func, 'run', func)
    description = getattr(func, GWFuncDesc._func_desc_attr, None)
    if description is None:
        raise MissingDescriptionException('Function is missing description decorators')
    return description


class Argument(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)


# No default value for this argument
class PositionalArg(Argument):
    pass


# Has a default argument for the value
class KeywordArg(Argument):
    pass


class VarsArg(Argument):
    pass


class KwargsArg(Argument):
    pass

# TODO: is there anything we want to try and do with the functions
# annotated return value?
# class Return(Argument): pass


def _clean_function_doc(f):
    doc = getdoc(f) or ''
    if isinstance(doc, bytes):
        doc = doc.decode('utf-8')
    return doc


class GWFuncDesc(object):
    _func_desc_attr = "_gw_function_description"
    _parameter_repr = ['POSITIONAL_ONLY',
                       'POSITIONAL_OR_KEYWORD',
                       'VAR_POSITIONAL',
                       'KEYWORD_ONLY',
                       'VAR_KEYWORD']

    VarsArgCls = VarsArg
    KwargsArgCls = KwargsArg
    PositionalArgCls = PositionalArg
    KeywordArgCls = KeywordArg

    @classmethod
    def get_description(cls, func):
        if cls.has_description(func) and \
           isinstance(getattr(func, cls._func_desc_attr), cls):
            return getattr(func, cls._func_desc_attr)
        return None

    @classmethod
    def has_description(cls, func):
        return hasattr(func, cls._func_desc_attr)

    @classmethod
    def set_description(cls, func):
        setattr(func, GWFuncDesc._func_desc_attr, cls(func))
        return None

    def __init__(self, func):
        self.func_name = func.__name__
        self.func_help = _clean_function_doc(func)
        self._metadata = {}
        self._signature = signature(func)

    def __repr__(self):
        parameters = []
        for name in self._signature.parameters:
            kind = self._signature.parameters[name].kind
            parameters.append("{}:{}".format(name, self._parameter_repr[kind]))

        return "<{}(".format(self.__class__.__name__) + ", ".join(parameters) + ")>"

    def __getitem__(self, key):
        return self._construct_argument(
            self._get_class(self._signature.parameters[key]), key)

    def _construct_argument(self, parameter_cls, name):
        p = self._signature.parameters[name]
        metadata = {}

        if p.default != p.empty:
            metadata['default'] = p.default
        if p.annotation != p.empty:
            # TODO: make sure annotation is a type and not just garbage
            metadata['data_type'] = p.annotation

        metadata.update(self._metadata.get(name, {}))

        return parameter_cls(name, **metadata)

    def _is_varargs(self, p):
        return p.kind == Parameter.VAR_POSITIONAL

    def _is_kwargs(self, p):
        return p.kind == Parameter.VAR_KEYWORD

    def _is_kwarg(self, p):
        return p.kind == Parameter.KEYWORD_ONLY or (
            p.kind == Parameter.POSITIONAL_OR_KEYWORD and p.default != p.empty)

    def _is_posarg(self, p):
        return p.kind == Parameter.POSITIONAL_ONLY or (
            p.kind == Parameter.POSITIONAL_OR_KEYWORD and p.default == p.empty)

    def _get_class(self, p):
        if self._is_varargs(p):
            return self.VarsArgCls
        elif self._is_kwargs(p):
            return self.KwargsArgCls
        elif self._is_posarg(p):
            return self.PositionalArgCls
        elif self._is_kwarg(p):
            return self.KeywordArgCls
        else:
            raise RuntimeError("Could not determine parameter type!")

    def init_metadata(self, name):
        if name not in self._metadata:
            self._metadata[name] = {}

    def set_metadata(self, name, key, value):
        if name not in self._signature.parameters:
            raise RuntimeError("{} is not a valid argument to this function!".format(name))

        self.init_metadata(name)

        self._metadata[name][key] = value

    @property
    def arguments(self):
        return [
            self._construct_argument(
                self._get_class(self._signature.parameters[name]), name)
            for name in self._signature.parameters]

    @property
    def varargs(self):
        for name in self._signature.parameters:
            if self._is_varargs(self._signature.parameters[name]):
                return self._construct_argument(VarsArg, name)
        return None

    @property
    def kwargs(self):
        for name in self._signature.parameters:
            if self._is_kwargs(self._signature.parameters[name]):
                return self._construct_argument(KeywordArg, name)
        return None

    @property
    def positional_args(self):
        return [arg for arg in self.arguments if isinstance(arg, PositionalArg)]

    @property
    def keyword_args(self):
        return [arg for arg in self.arguments if isinstance(arg, KeywordArg)]


def parameter(name, **kwargs):
    if not isinstance(name, six.string_types):
        raise TypeError('Expected argument name to be a string')

    data_type = kwargs.get("data_type", None)
    if callable(data_type):
        kwargs['data_type'] = data_type(name, **kwargs)

    def argument_wrapper(func):
        if not GWFuncDesc.has_description(func):
            GWFuncDesc.set_description(func)

        desc = GWFuncDesc.get_description(func)

        # Make sure the metadata key exists even if we don't set any
        # values on it.  This ensures that metadata's keys represent
        # the full list of parameters that have been identified by the
        # user (even if there is no actual metadata associated with
        # the argument).
        desc.init_metadata(name)

        for key, value in six.iteritems(kwargs):
            desc.set_metadata(name, key, value)

        return func

    return argument_wrapper


@deprecation.deprecated(deprecated_in="0.8.5", removed_in="0.9.0",
                        current_version=__version__,
                        details="Use 'parameter' decorator instead")
def argument(name, data_type, *args, **kwargs):
    """Describe an argument to a function as a function decorator.

    Additional arguments are passed to the type class constructor.

    :param str name: The parameter name from the function declaration
    :param type: A type class derived from ``girder_worker_utils.types.Base``
    """
    if not isinstance(name, six.string_types):
        raise TypeError('Expected argument name to be a string')

    if callable(data_type):
        data_type = data_type(name, *args, **kwargs)

    def argument_wrapper(func):
        setattr(func, GWFuncDesc._func_desc_attr,
                getattr(func, GWFuncDesc._func_desc_attr, {}))

        args = getattr(func, GWFuncDesc._func_desc_attr).setdefault('arguments', [])
        sig = signature(func)

        if name not in sig.parameters:
            raise ValueError('Invalid argument name "%s"' % name)

        data_type.set_parameter(sig.parameters[name], signature=sig)
        args.insert(0, data_type)

        def call_item_task(inputs, outputs={}):
            args, kwargs = parse_inputs(func, inputs)
            return func(*args, **kwargs)

        def describe():
            return describe_function(func)

        func.call_item_task = call_item_task
        func.describe = describe

        return func

    return argument_wrapper


def describe_function(func):
    """Return a json description from a decorated function."""
    description = get_description_attribute(func)

    inputs = [arg.describe() for arg in description.get('arguments', [])]
    spec = {
        'name': description.get('name', func.__name__),
        'inputs': inputs,
        'mode': 'girder_worker'
    }
    desc = description.get('description', getdoc(func))
    if desc:
        spec['description'] = desc

    return spec


def get_input_data(arg, input_binding):
    """Parse an input binding from a function argument description.

    :param arg: An instantiated type description
    :param input_binding: An input binding object
    :returns: The parameter value
    """
    mode = input_binding.get('mode', 'inline')
    if mode == 'inline' and 'data' in input_binding:
        value = arg.deserialize(input_binding['data'])
    elif mode == 'girder':
        value = input_binding.get('id')
    else:
        raise ValueError('Unhandled input mode')

    arg.validate(value)
    return value


def parse_inputs(func, inputs):
    """Parse an object of input bindings from item_tasks.

    :param func: The task function
    :param dict inputs: The input task bindings object
    :returns: args and kwargs objects to call the function with
    """
    description = get_description_attribute(func)
    arguments = description.get('arguments', [])
    args = []
    kwargs = {}
    for arg in arguments:
        desc = arg.describe()
        input_id = desc['id']
        name = desc['name']
        if input_id not in inputs and not arg.has_default():
            raise MissingInputException('Required input "%s" not provided' % name)
        if input_id in inputs:
            kwargs[name] = get_input_data(arg, inputs[input_id])
    return args, kwargs
