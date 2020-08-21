import typing as tp


def get_attribute(v, attr: tp.Optional[str] = None):
    if attr is not None:
        return v
    else:
        return getattr(v, attr)
