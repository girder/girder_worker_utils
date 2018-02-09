import click


class Parameter(click.Option):
    _item_tasks_type = None

    def item_tasks_json(self, command=None):
        spec = {
            'id': self.name,
            'name': self.name,
            'description': self.help or ''
        }
        spec.update(self.type.item_tasks_json(self))
        return spec

    def is_input(self):
        return self._item_tasks_type == 'input'

    def is_output(self):
        return self._item_tasks_type == 'output'
