import click


class String(click.types.StringParamType):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'string'
        }
