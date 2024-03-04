class SetZip:
    """
    An object which zips a bunch of sets together.

    Ie. checks for inclusion by checking each set.

    Also supports len and iteration protocol.

    You can also add extra sets:

    >>> c = SetZip()
    >>> c += set([1, 2, 3])

    Provided arguments must implement contains, length and iter.
    """

    def __iadd__(self, other: set):
        self.args.append(other)
        return self

    def __init__(self, *args: set):
        self.args = list(args)

    def __contains__(self, item) -> bool:
        return any(item in arg for arg in self.args)

    def __len__(self) -> int:
        return sum(len(arg) for arg in self.args)

    def __iter__(self):
        for arg in self.args:
            yield from arg
