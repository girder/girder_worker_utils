from click.exceptions import BadParameter

from .parameter import Parameter


class Output(Parameter):
    _item_tasks_type = 'output'

    def get_result_hook(self, bindings, ctx, inputs={}):
        if not hasattr(self.type, 'generate_result_hook'):
            return

        if self.name in bindings:
            binding = bindings[self.name]

            if not isinstance(binding, dict):
                raise BadParameter('Invalid output binding', ctx=ctx, param=self)

            return self.type.generate_result_hook(
                binding, param=self, ctx=ctx, bindings=bindings, inputs=inputs)
