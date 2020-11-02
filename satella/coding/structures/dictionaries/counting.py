import typing as tp


class CountingDict:
    """
    A dictionary to quickly count the amount of elements in a set

    :param set_to_count: a sequence, whose elements should be counted.
        The elements should support being keys in a dictionary.
    """
    __slots__ = ('dct',)

    def __init__(self, set_to_count: tp.Sequence = ()):
        self.dct = {}
        for elem in set_to_count:
            self.count(elem)

    def __getitem__(self, item):
        return self.dct[item]

    def count(self, elem, pieces: int = 1) -> None:
        """
        Add an instance of elem to the set

        :param elem: instance to add
        :param pieces: amount to add
        """
        if elem not in self.dct:
            self.dct[elem] = pieces
        else:
            self.dct[elem] += pieces

    def clear(self):
        self.dct = {}

    def keys(self):
        return self.dct.keys()

    def values(self):
        return self.dct.values()

    def items(self):
        return self.dct.items()

    def __iter__(self):
        return iter(self.dct)

    def __len__(self):
        return len(self.dct)

    def __bool__(self):
        return bool(self.dct)
