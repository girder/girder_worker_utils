try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

from click.exceptions import BadParameter

from .parameter import Parameter


class Input(Parameter):
    _item_tasks_type = 'input'

    # TODO: Currently, the context argument exists entirely to provide the function
    #       signature for providing default values.  Click on it's own expects that
    #       defaults are provided by the @option decorators.  It could be that parsing
    #       the function signature for default values is a bad idea, and we should
    #       remove the context argument here.
    #
    #       As an additional implementation note, there is some confusion as to
    #       exactly methods need to have access to the context.  In most cases,
    #       click uses the context optionally inside it's API.  In the item_tasks
    #       use case, it is complicated because we cannot create a context (which
    #       requires the argument list) before parsing the input bindings.  This
    #       will almost certainly cause pain down the road as code is created that
    #       *needs* access to the context for special processing.
    def item_tasks_json(self, ctx=None):
        spec = super(Input, self).item_tasks_json(ctx)

        # get default from the decorator
        default = self.get_default(ctx)

        # get default from the function definition
        if ctx and self.default is None:
            default = self._get_default_from_function(ctx.command)

        if default is not None:
            spec['default'] = {
                'data': default
            }
        spec.update(self.type.item_tasks_json(self, ctx))
        return spec

    def get_kwargs_from_input_bindings(self, bindings, ctx):
        value = self.default
        if self.name in bindings:
            binding = bindings[self.name]
            if not isinstance(binding, dict):
                raise BadParameter('Invalid input binding', ctx=ctx, param=self)

            value = binding
            if binding.get('mode', 'inline') == 'inline':
                value = binding['data']

            if hasattr(self.type, 'resolve_item_tasks_binding'):
                value = self.type.resolve_item_tasks_binding(
                    value, param=self, ctx=ctx, bindings=bindings)

        if value is None:
            return {}

        return {self.name: value}

    def _get_default_from_function(self, command):
        if command is None:
            return
        func = command.callback
        sig = signature(func)
        if self.name not in sig.parameters:
            return
        param = sig.parameters[self.name]
        if param.default == param.empty:
            return
        return param.default
