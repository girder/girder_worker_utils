import json

import click

from .parameter import Parameter


class Command(click.Command):

    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params', None) or []
        input_params = []
        output_params = []
        other_params = []
        for param in params:
            if isinstance(param, Parameter) and param.is_input():
                input_params.append(param)
            elif isinstance(param, Parameter) and param.is_output():
                output_params.append(param)
            else:
                other_params.append(param)
        other_params += [
            click.Option(('--item-tasks-json',), is_flag=True, default=False)
        ]
        kwargs['params'] = input_params + other_params
        self._input_params = input_params
        self._output_params = output_params
        self._other_params = other_params
        super(Command, self).__init__(*args, **kwargs)

    def invoke(self, ctx):
        if ctx.params.pop('item_tasks_json', False):
            return self._print_item_tasks_json(ctx)
        return super(Command, self).invoke(ctx)

    def invoke_item_task(self, bindings):
        # parse the input bindings to construct an argument list
        kwargs = {}

        # We need to loop through all of the input_params to get default values
        # because we are bypassing the part of click that does this by calling
        # ctx.invoke directly.  This is done because there is no way to
        # construct CLI argument list from bindings (the name munging logic in
        # click is strictly one directional).
        #
        # Alternatively, we might store the commandline argument name in addition
        # to the bound variable name so we *can* generate a valid CLI argument
        # list... this could potentially remove some of the custom logic present
        # in girder's item_tasks plugin.
        with self.make_context(self.name, [], resilient_parsing=True) as ctx:
            for param in self._input_params:
                kwargs.update(param.get_kwargs_from_input_bindings(bindings, ctx))

            return ctx.invoke(self.callback, **kwargs)

    def parse_inputs(self, bindings):
        # similar to the above... should be deduped somehow
        kwargs = {}
        with self.make_context(self.name, [], resilient_parsing=True) as ctx:
            for param in self._input_params:
                kwargs.update(param.get_kwargs_from_input_bindings(bindings, ctx))

        return [], kwargs

    def item_tasks_json(self, ctx=None):
        spec = {
            'name': self.name,
            'description': self.help or '',
            'mode': 'girder_worker',
            'inputs': [],
            'outputs': []
        }
        for param in self._input_params:
            spec['inputs'].append(param.item_tasks_json(ctx))
        for param in self._output_params:
            spec['outputs'].append(param.item_tasks_json(ctx))
        return spec

    def make_context(self, info_name, args, **kwargs):
        if '--item-tasks-json' in args:
            kwargs.setdefault('resilient_parsing', True)
        return super(Command, self).make_context(info_name, args, **kwargs)

    def _print_item_tasks_json(self, ctx=None):
        spec = self.item_tasks_json(ctx)
        click.echo(json.dumps(spec, indent=2))
