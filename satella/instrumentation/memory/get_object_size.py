import sys


# shamelessly stolen from
# https://goshippo.com/blog/measure-real-size-any-python-object/
def get_size(obj, seen=None) -> int:
    """
    Recursively finds the total size of an object (object + it's components).

    :param obj: object to measure
    :return: size in bytes of the object and all of it's subcomponents
    :raises RuntimeError: when ran on PyPy
    """
    try:
        size = sys.getsizeof(obj)
    except TypeError:
        raise RuntimeError('Running on PyPy?')
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_size(v, seen) for v in obj.values())
        size += sum(get_size(k, seen) for k in obj.keys())
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_size(i, seen) for i in obj)
    return size
