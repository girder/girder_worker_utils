import sys

from girder_worker_utils.tee import TeeStdErr, TeeStdOut


class TeeCapture(TeeStdOut):
    def __init__(self, *args, **kwargs):
        self.buf = ''
        super(TeeCapture, self).__init__(*args, **kwargs)

    def write(self, message, **kwargs):
        self.buf += message
        super(TeeCapture, self).write(message, **kwargs)


def test_tee_sys_write_stdout(capfd):
    with TeeStdOut():
        sys.stdout.write('Test String')
        sys.stdout.flush()

    out, err = capfd.readouterr()
    assert out == 'Test String'


def test_tee_print_stdout(capfd):
    with TeeStdOut():
        print('Test String')

    out, err = capfd.readouterr()
    assert out == 'Test String\n'


def test_tee_stdout_sys_write_pass_through_false(capfd):
    with TeeStdOut(pass_through=False):
        sys.stdout.write('Test String')
        sys.stdout.flush()

    out, err = capfd.readouterr()
    assert out == ''


def test_tee_stdout_print_pass_through_false(capfd):
    with TeeStdOut(pass_through=False):
        print('Test String')

    out, err = capfd.readouterr()
    assert out == ''


def test_tee_sys_write_stderr(capfd):
    with TeeStdErr():
        sys.stderr.write('Test String')
        sys.stderr.flush()

    out, err = capfd.readouterr()
    assert err == 'Test String'


def test_tee_stderr_sys_write_pass_through_false(capfd):
    with TeeStdErr(pass_through=False):
        sys.stderr.write('Test String')
        sys.stderr.flush()

    out, err = capfd.readouterr()
    assert err == ''


def test_tee_overwrites_write(capfd):
    with TeeCapture() as o:
        print('Test String')
        assert o.buf == 'Test String\n'

    out, err = capfd.readouterr()
    assert out == 'Test String\n'


def test_tee_overwrites_write_pass_through_false(capfd):
    with TeeCapture(pass_through=False) as o:
        print('Test String')
        assert o.buf == 'Test String\n'

    out, err = capfd.readouterr()
    assert out == ''
