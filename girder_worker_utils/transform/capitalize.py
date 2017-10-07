from .base import Transform


class Capitalize(Transform):
    def __init__(self, value):
        self.value = value

    def transform(self):
        return self.value.upper()
