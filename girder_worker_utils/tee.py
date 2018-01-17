import abc
import sys

import six


def _set_stdout(stream):
    """Set sys.stdout to a new file-like object.

    This is a private function for re-assigning sys.stdout. It returns
    the old value of sys.stdout.

    """
    old = sys.stdout
    sys.stdout = stream
    return old


def _set_stderr(stream):
    """Set sys.stderr to a new file-like object.

    This is a private function for re-assigning sys.stderr. It returns
    the old value of sys.stderr.

    """
    old = sys.stderr
    sys.stderr = stream
    return old


@six.add_metaclass(abc.ABCMeta)
class Tee(object):
    @staticmethod
    @abc.abstractmethod
    def set_stream(stream):
        pass

    def __init__(self, pass_through=True):
        self.pass_through = pass_through
        self._original = self.set_stream(self)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __del__(self):
        # Clean set the stream back to the original on deletion. This
        # prevents losing the original stream object, and also makes
        # subclasses very ammenable to contextmanagers.
        self.set_stream(self._original)

    def __getattr__(self, attr):
        return getattr(self._original, attr)

    def write(self, *args, **kwargs):
        if self.pass_through:
            self._original.write(*args, **kwargs)

    def flush(self, *args, **kwargs):
        if self.pass_through:
            self._original.flush(*args, **kwargs)


class TeeStdOut(Tee):
    set_stream = staticmethod(_set_stdout)


class TeeStdErr(Tee):
    set_stream = staticmethod(_set_stderr)
