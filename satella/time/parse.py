import typing as tp

TIME_MODIFIERS = [
    ('s', 1),
    ('m', 60),
    ('h', 60 * 60),
    ('d', 24 * 60 * 60),
    ('w', 7 * 24 * 60 * 60)
]


def parse_time_string(s: tp.Union[int, float, str]) -> float:
    """
    Parse a time string into seconds, so eg. '30m' will be equal to 1800, and so will
    be '30 min'.

    This will correctly parse:
    - seconds
    - minutes
    - hours
    - days
    - weeks

    .. warning:: This does not handle fractions of a second!

    :param s: time string or time value in seconds
    :return: value in seconds
    """
    if isinstance(s, (int, float)):
        return s

    for modifier, multiple in TIME_MODIFIERS:
        if modifier in s:
            return float(s[:s.index(modifier)]) * multiple

    return float(s)
