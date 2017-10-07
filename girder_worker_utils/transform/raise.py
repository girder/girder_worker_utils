from kombu.exceptions import DecodeError

from .transform import Transform


class Raise(Transform):

    def transform(self):
        raise DecodeError("Some kind of Error")
