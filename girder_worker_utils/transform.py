import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Transform(object):
    def __init__(self, *args, **kwargs):
        pass

    def model_repr(self):
        """
        This method is called before save the argument in the job model.
        """
        return str(self)

    def cleanup(self):
        pass

    @abc.abstractmethod
    def transform(self):
        pass
