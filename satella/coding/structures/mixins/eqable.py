from ..immutable import NOT_EQUAL_TO_ANYTHING


class DictionaryEQAble:
    """
    A class mix-in that defines __eq__ and __ne__ to be:

    - both the same exact type (so subclassing won't work)
    - have the exact same __dict__
    """

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        for key in self.__dict__.keys():
            if getattr(other, key, NOT_EQUAL_TO_ANYTHING) != self.__dict__[key]:
                return False
        return True

    def __ne__(self, other) -> bool:
        if type(self) != type(other):
            return True
        for key in self.__dict__.keys():
            if getattr(other, key, NOT_EQUAL_TO_ANYTHING) != self.__dict__[key]:
                return True
        return False
