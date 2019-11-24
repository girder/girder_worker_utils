import six

collect_ignore = []
if six.PY2:
    collect_ignore.append("py3_decorators_test.py")
