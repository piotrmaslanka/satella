import collections


class DefaultDict(collections.defaultdict):
    """
    A collections.defaultdict that does not store in itself empty values that it generates
    """

    def __getitem__(self, item):
        if item not in self:
            return self.default_factory()
        return super().__getitem__(item)
