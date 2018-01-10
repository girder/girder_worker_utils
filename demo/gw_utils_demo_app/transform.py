from kombu.exceptions import DecodeError

from girder_worker_utils.transform import Transform


class Capitalize(Transform):
    def transform(self):
        return self.value.upper()


class RaiseException(Transform):

    def transform(self):
        raise DecodeError('Some kind of Error')


class Reverse(Transform):
    def transform(self):
        return self.value[::-1]
