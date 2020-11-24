import typing as tp

from satella.coding.typing import K


def hashables_to_int(words: tp.List[K]) -> tp.Dict[K, int]:
    """
    Assign each hashable an integer, starting from 0, and return the resulting mapping

    :param words: a list of hashables
    :return: a dictionary keyed by hashable and values are the assigned integers
    """
    dictionary = {}
    i = 0
    for word in set(words):
        dictionary[word] = i
        i += 1
    return dictionary
