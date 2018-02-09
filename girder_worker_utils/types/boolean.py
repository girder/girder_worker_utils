import click


class Boolean(click.types.BoolParamType):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'boolean'
        }
