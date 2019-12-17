import typing as tp

__all__ = ['DictObject', 'apply_dict_object']


class DictObject(dict):
    def __getattr__(self, item: str) -> tp.Any:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(repr(e))

    def __setattr__(self, key: str, value: tp.Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(repr(e))


def apply_dict_object(v: tp.Any) -> tp.Union[DictObject, tp.Any]:
    """
    Apply DictObject() to every dict inside v.

    This assumes that the only things that will be touched will be nested dicts and lists.

    If you pass a non-dict and a non-list, they will be returned as is.
    """
    if isinstance(v, list):
        return [apply_dict_object(x) for x in v]
    elif isinstance(v, dict):
        return DictObject({
            k: apply_dict_object(val) for k, val in v.items()
        })
    else:
        return v
