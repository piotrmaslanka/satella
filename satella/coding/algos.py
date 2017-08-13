# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import types
import copy
import itertools
from .typecheck import typed


def _merge(v1, v2):
    if isinstance(v1, list) and isinstance(v2, list):
        return v1 + v2
    elif isinstance(v1, dict) and isinstance(v2, dict):
        v1.update(v2)
        return v1
    else:
        raise TypeError


@typed(dict, dict, returns=dict)
def merge_dicts(first, second):
    for key in second.keys():
        try:
            first[key] = _merge(first[key], second[key])
        except (TypeError, KeyError):       # overwrite, not a list or dict, or no key in first
            first[key] = second[key]

    return first
