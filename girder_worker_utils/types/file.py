import click

from ..transforms.girder_io import GirderFileId, GirderFolderId, GirderUploadToFolder


class File(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        widget = 'file'
        if param.is_output():
            widget = 'new-file'
        return {
            'type': widget
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        return GirderFileId(value['_id'])

    def generate_result_hook(self, value, param, **kwargs):
        return GirderUploadToFolder(value['parent_id'], value['name'])


class Image(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        return {
            'type': 'image'
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        return GirderFileId(value['_id'])

    def generate_result_hook(self, value, param, **kwargs):
        return GirderUploadToFolder(value['parent_id'], value['name'])


class Folder(click.types.Path):
    def item_tasks_json(self, param, ctx=None):
        widget = 'directory'
        if param.is_output():
            widget = 'new-folder'
        return {
            'type': widget
        }

    def resolve_item_tasks_binding(self, value, param, **kwargs):
        return GirderFolderId(value['_id'])

    def generate_result_hook(self, value, param, **kwargs):
        return GirderUploadToFolder(value['parent_id'], value['name'])
