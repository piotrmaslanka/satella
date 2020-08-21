import typing as tp


def p_all(*args: tp.Callable[[tp.Any], bool]) -> tp.Callable[[tp.Any], bool]:
    """
    Make a predicate returning True if all specified predicates return True
    """
    def predicate(v):
        return all(arg(v) for arg in args)
    return predicate


def p_any(*args: tp.Callable[[tp.Any], bool]) -> tp.Callable[[tp.Any], bool]:
    """
    Make a predicate returning True if any of specified predicates return True
    """
    def predicate(v):
        return any(arg(v) for arg in args)
    return predicate


def attribute(p: tp.Callable[[tp.Any], bool], attr) -> tp.Callable[[tp.Any], bool]:
    """
    Make predicate p refer to attribute of the object passed to it.
    """
    def predicate(v):
        return p(getattr(v, attr))
    return predicate


def item(p: tp.Callable[[tp.Any], bool], i) -> tp.Callable[[tp.Any], bool]:
    """
    Make predicate p refer to i-th item of the value passed to it

    i doesn't have to be an integer, it will be passed to __getitem__
    """
    def predicate(v):
        return p(v[i])
    return predicate

