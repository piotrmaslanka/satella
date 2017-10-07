# coding=UTF-8
from __future__ import print_function, absolute_import, division

from .typecheck import typed


def _merge(v1, v2):
    if isinstance(v1, dict) and isinstance(v2, dict):
        for k in v2.keys():
            try:
                v1[k] = _merge(v1[k], v2[k])
            except KeyError:
                v1[k] = v2[k]
        return v1

    if isinstance(v1, list) and isinstance(v2, list):
        v1.extend(v2)
        return v1

    return v2


@typed(dict, dict, returns=dict)
def merge_dicts(first, second):
    return _merge(first, second)
