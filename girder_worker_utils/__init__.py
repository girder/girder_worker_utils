import argparse
import json

__version__ = '0.1.0'


def _convert_cli_args(args, known_args):
    # TODO type conversion (for now everything's a string)
    return {known['id']: getattr(args, known['id']) for known in known_args}


def task_cli(cli):
    pass # TODO single CLI in a script


def task_clis(clis, name=None, description=None):
    name = name or 'CLIs'
    parser = argparse.ArgumentParser(prog=name, description=description)
    # TODO add --girder-task arg to top level that will print out full list
    subparsers = parser.add_subparsers(dest='cli', help='sub-command help')
    subcmd_map = {}

    for cli in clis:
        sub = subparsers.add_parser(cli.__name__, help=cli._worker_task_description)
        sub.add_argument('--girder-task', action='store_true')

        arg_list = cli._worker_task_spec['inputs'] + cli._worker_task_spec['outputs']

        for arg in arg_list:
            # TODO support boolean inputs as flags
            sub.add_argument(
                '--' + arg['id'], help=arg['description'],
                default=arg.get('default', {}).get('data'))

        subcmd_map[cli.__name__] = {
            'fn': cli,
            'args': arg_list
        }

    args = parser.parse_args()
    val = subcmd_map[args.cli]

    if args.girder_task:
        print(json.dumps(val['fn']._worker_task_spec))
    else:
        val['fn'](**_convert_cli_args(args, val['args']))


class Input(object):
    def __init__(self, id, name=None, description='', required=True, type='string', default=None):
        self.id = id
        self.name = name
        self.description = description
        self.required = required
        self.type = type
        self.default = default

        self.dict = {
            'id': id,
            'name': name if name is not None else id,
            'description': description,
            'type': type
        }

        if default is not None:
            self.dict['default'] = {'data': default}


class Output(object):
    def __init__(self, id, name=None, description='', required=True, type='string'):
        self.id = id
        self.name = name
        self.description = description
        self.required = required
        self.type = type

        self.dict = {
            'id': id,
            'name': name if name is not None else id,
            'description': description,
            'type': type
        }


class task(object):
    def __init__(self, mode, name, description, inputs=None, outputs=None):
        self.name = name
        self.description = description
        self.inputs = inputs or []
        self.outputs = outputs or []
        self._spec = {
            'mode': mode,
            'inputs': [i.dict for i in self.inputs],
            'outputs': [o.dict for o in self.outputs]
        }

    def __call__(self, fn):
        fn._worker_task_name = self.name
        fn._worker_task_description = self.description
        fn._worker_task_spec = self._spec

        return fn


class docker_task(task):
    def __init__(self, image, pull=True, *args, **kwargs):
        super(docker_task, self).__init__(mode='docker', *args, **kwargs)

        self._spec['docker_image'] = image
        self._spec['pull_image'] = pull
        self._spec['container_args'] = [self._arg(io) for io in self.inputs + self.outputs]

    def _arg(self, io_spec):
        if isinstance(io_spec, Input):
            token = '$input'
        elif isinstance(io_spec, Output):
            token = '$output'
        else:
            raise Exception('Unknown input or output specification: %r' % io_spec)

        return '--%s=%s{%s}' % (io_spec.id, token, io_spec.id)
