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
    >>> c = permute_together(a, b)

    Might equal

    >>> c == [[3, 1, 2], ['c', 'a', 'b']]
    """

    indices = list(range(len(args[0])))

    random.shuffle(indices)
    return [[arg[i] for arg, i in zip(arg, indices)] for arg in args]
