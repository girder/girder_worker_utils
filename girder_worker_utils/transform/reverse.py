from .base import Transform


class Reverse(Transform):
    def __init__(self, value):
        self.value = value

    def transform(self):
        return self.value[::-1]
