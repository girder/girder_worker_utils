import click


class File(click.types.File):
    def item_tasks_json(self, param, ctx=None):
        widget = 'file'
        if param.is_output():
            widget = 'new-file'
        return {
            'type': widget
        }


class Image(click.types.File):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'image'
        }


class Folder(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        widget = 'directory'
        if param.is_output():
            widget = 'new-folder'
        return {
            'type': widget
        }
