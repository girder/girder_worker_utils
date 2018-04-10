import click

from .command import Command
from .input import Input
from .output import Output
from .types import String


def task(name=None, cls=Command, **attrs):
    def wrapper(func):
        cmd_wrapper = click.command(name, cls, **attrs)
        func.main = cmd_wrapper(func)
        func.call_item_task = func.main.invoke_item_task
        func.describe = func.main.item_tasks_json
        return func
    return wrapper


def task_input(*param_decls, **attrs):
    attrs.setdefault('cls', Input)
    attrs.setdefault('type', String())
    return click.option(*param_decls, **attrs)


def task_output(*param_decls, **attrs):
    decls = []
    for decl in param_decls:
        if not decl.startswith('-'):
            decl = '--' + decl
        decls.append(decl)
    attrs.setdefault('cls', Output)
    attrs.setdefault('type', String())
    return click.argument(*decls, **attrs)


def get_item_tasks_description(func):
    if not hasattr(func, 'main') or not hasattr(func.main, 'item_tasks_json'):
        raise MissingDescriptionException
    return func.main.item_tasks_json()


class MissingDescriptionException(Exception):
    pass
