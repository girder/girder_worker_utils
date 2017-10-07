from kombu.exceptions import DecodeError

from .base import Transform


class RaiseException(Transform):

    def transform(self):
        raise DecodeError("Some kind of Error")
