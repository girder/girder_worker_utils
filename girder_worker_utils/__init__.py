import six

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


def _walk_obj(obj, func, leaf_condition=None):
    """Walk through a nested object applying func to each leaf element.

    This function returns a recursively built structure from a nested
    tree of simple container types (e.g. dict, list, tuple) by
    applying func to each leaf node in the tree. By default a leaf
    node is considered to be any object that is not a dict, list or
    tuple.

    leaf_condition may be used if certain types of lists, tuples or
    dicts should be considered leaf nodes. leaf_condition should be
    passed a function that takes a sub-tree and returns True if that
    sub-tree is a leaf node, or False if _walk_obj should continue to
    descend through the sub-tree.

    """
    if hasattr(leaf_condition, '__call__'):
        if leaf_condition(obj):
            return func(obj)

    if isinstance(obj, dict):
        return {k: _walk_obj(v, func, leaf_condition=leaf_condition)
                for k, v in six.viewitems(obj)}

    elif isinstance(obj, list):
        return [_walk_obj(v, func, leaf_condition=leaf_condition) for v in obj]

    elif isinstance(obj, tuple):
        return tuple(_walk_obj(list(obj), func, leaf_condition=leaf_condition))

    return func(obj)
