import random
import typing as tp

__all__ = ['shuffle_together']


def shuffle_together(*args: tp.Sequence) -> tp.List[tp.List]:
    """
    args, being sequences of equal length, will be permuted in such a way
    that their indices will still correspond to each other.

    So given:

    >>> a = [1, 2, 3]
    >>> b = ['a', 'b', 'c']
    >>> c = shuffle_together(a, b)

    Might equal

    >>> c == [[3, 1, 2], ['c', 'a', 'b']]

    """
    try:
        indices = list(range(len(args[0])))
    except IndexError:
        return []  # empty array

    random.shuffle(indices)
    return [[arg[i] for i in indices] for arg in args]
