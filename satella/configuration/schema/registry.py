BASE_LOOKUP_TABLE = {}
PLAIN_ENTRIES = set()


def register_custom_descriptor(name: str, is_plain: bool = True):
    """
    A decorator used for registering custom descriptors in order to be loadable via
    descriptor_from_dict

    Use like:

    >>> @register_custom_descriptor('ipv6')
    >>> class IPv6(Regexp):
    >>>     REGEXP = '(([0-9a-f]{1,4}:)' ...

    :param name: under which it is supposed to be invokable
    :param is_plain: is this a nested structure?
    """

    def inner(cls):
        global BASE_LOOKUP_TABLE, PLAIN_ENTRIES
        if is_plain:
            PLAIN_ENTRIES.add(name)
        BASE_LOOKUP_TABLE[name] = cls
        return cls

    return inner
