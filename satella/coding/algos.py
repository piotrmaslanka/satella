# coding=UTF-8
from __future__ import print_function, absolute_import, division


def merge_dicts(v1, v2):
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
