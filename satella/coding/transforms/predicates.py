import typing as tp


def is_subset(subset: tp.Dict, superset: tp.Dict) -> bool:
    """
    Does superset contain all keys of subset, and are their values equal?

    :param subset: the set that contains all the keys
    :param superset: the set that is to contain all the keys in subset, and their values
        have to be equal
    :return: does the condition hold?
    """
    for k, v in subset.items():
        if k not in superset:
            return False
        if v != superset[k]:
            return False
    return True
