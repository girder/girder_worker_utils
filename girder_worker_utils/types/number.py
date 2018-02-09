import click


class Integer(click.types.IntRange):
    def __init__(self, widget='number', step=1, **kwargs):
        self.widget = widget
        self.step = step
        super(Integer, self).__init__(**kwargs)

    def item_tasks_json(self, param, ctx=None):
        widget = self.widget
        if param.nargs > 1:
            widget = 'number-vector'
        return {
            'type': widget,
            'min': self.min,
            'max': self.max,
            'step': self.step
        }


# click.FloatRange is created in click master, but not released.
# We could consider backporting it to support min/max arguments
# and slider widgets.
class Float(click.types.FloatParamType):
    def item_tasks_json(self, param, ctx=None):
        widget = 'number'
        if param.nargs > 1:
            widget = 'number-vector'
        return {
            'type': widget
        }
