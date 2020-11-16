import base64


def b64encode(content: bytes) -> str:
    """
    Syntactic sugar for:

    >>> import base64
    >>> y = base64.b64encode(content).decode('utf-8')

    Since `base64.b64decode(str)` returns bytes, the reverse is not provided.

    :param content: content to encode
    :return: content encoded as a string
    """
    return base64.b64encode(content).decode('utf-8')
