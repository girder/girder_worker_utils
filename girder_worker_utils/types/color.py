import click


class Color(click.types.StringParamType):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'color'
        }
