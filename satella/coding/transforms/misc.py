import typing as tp

from satella.coding.typing import V


def list_values_to_indices(lst: tp.List[V]) -> tp.Dict[V, int]:
    """
    Transform a list of entries into a dict mapping where given entry can be found.

    Example:

    >>> a = ['abc', 'def', 'ghi']
    >>> b = list_values_to_indices(a)
    >>> assert b == {'abc': 0, 'def': 1, 'ghi': 2}

    :param lst: list to process. Take care for the list to be composed of unique entries.
    :raises ValueError: item was found more than once
    """
    result = {}
    for idx, val in enumerate(lst):
        if val in result:
            raise ValueError(f'Entry {val} found more than once!')
        result[val] = idx
    return result
