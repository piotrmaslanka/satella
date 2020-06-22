def update_if_not_none(dictionary: dict, key, value):
    """
    Syntactic sugar for

    >>> if value is not None:
    >>>     dictionary[key] = value

    :param dictionary: dictionary to update
    :param key: key to use
    :param value: value to use
    :return: the dictionary itself
    """
    if value is not None:
        dictionary[key] = value
    return dictionary
