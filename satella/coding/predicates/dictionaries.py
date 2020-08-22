import typing as tp


def has_keys(*keys: tp.Any) -> tp.Callable[[tp.Dict], bool]:
    """
    Return a predicate to check if your dictionary has all of given keys
    """
    def predicate(v: tp.Dict) -> bool:
        for key in keys:
            if key not in v:
                return False
        return True
    return predicate

