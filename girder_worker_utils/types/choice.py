import click


class Choice(click.Choice):

    def item_tasks_json(self, param, ctx=None):
        multiple = ''
        if param.multiple:
            multiple = '-multiple'
        return {
            'type': 'string-choice' + multiple,
            'values': self.choices
        }
