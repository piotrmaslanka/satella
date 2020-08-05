import typing as tp
import warnings


def update_if_not_none(dictionary: dict, key, value):
    """
    Deprecated alias for :func:`update_key_if_none`
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0,'
                  'use update_key_if_not_none instead', DeprecationWarning)
    return update_key_if_none(dictionary, key, value)


def update_attr_if_none(obj: object, attr: str, value: tp.Any,
                        on_attribute_error: bool = True,
                        if_value_is_not_none: bool = False) -> None:
    """
    Updates the object attribute, if it's value is None, or if
    it yields AttributeError (customizable as per on_attribute_error parameter)

    :param obj: object to alter
    :param attr: attribute to set
    :param value: value to set
    :param on_attribute_error: whether to proceed with setting the value on
        AttributeError while trying to read given attribute. If False, AttributeError
        will be raised.
    :param if_value_is_not_none: update object unconditionally, if only value is not None
    """
    if if_value_is_not_none:
        if value is not None:
            setattr(obj, attr, value)
    else:
        try:
            val = getattr(obj, attr)
            if val is None:
                setattr(obj, attr, value)
        except AttributeError:
            if on_attribute_error:
                setattr(obj, attr, value)
            else:
                raise


def update_key_if_none(dictionary: dict, key, value):
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
