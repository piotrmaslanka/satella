import typing as tp

__all__ = ['merge_dicts']


def merge_dicts(v1: tp.Any, v2: tp.Any) -> tp.Any:
    if isinstance(v1, dict) and isinstance(v2, dict):
        for k in v2.keys():
            try:
                v1[k] = merge_dicts(v1[k], v2[k])
            except KeyError:
                v1[k] = v2[k]
        return v1

    if isinstance(v1, list) and isinstance(v2, list):
        v1.extend(v2)
        return v1

    return v2
