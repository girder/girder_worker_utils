import click

from ..transforms.girder_io import GirderFileId, GirderFolderId


class File(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        widget = 'file'
        if param.is_output():
            widget = 'new-file'
        return {
            'type': widget
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        if param.is_output():
            return value

        return GirderFileId(value['_id'])


class Image(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'image'
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        if param.is_output():
            return value

        return GirderFileId(value['_id'])


class Folder(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        widget = 'directory'
        if param.is_output():
            widget = 'new-folder'
        return {
            'type': widget
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        if param.is_output():
            return value

        return GirderFolderId(value['_id'])
