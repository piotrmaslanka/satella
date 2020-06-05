BASE_LOOKUP_TABLE = {}


def register_custom_descriptor(name: str):
    """
    A decorator used for registering custom descriptors in order to be loadable via
    descriptor_from_dict

    Use like:

    >>> @register_custom_descriptor('ipv6')
    >>> class IPv6(Regexp):
    >>>     REGEXP = '(([0-9a-f]{1,4}:)' ...

    :param name: under which it is supposed to be invokable
    """

    def inner(cls):
        BASE_LOOKUP_TABLE[name] = cls
        return cls

    return inner
