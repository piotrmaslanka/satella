import typing as tp

__all__ = ['stringify_dict']


def stringify_dict(dct: dict, stringify: tp.Callable[[tp.Any], str]) -> tp.Dict[str, str]:
    return {stringify(k): stringify(v) for k, v in dct.items()}
