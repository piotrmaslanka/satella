# coding=UTF-8
"""
Base process
"""
from __future__ import print_function, absolute_import, division
import six
import logging

logger = logging.getLogger(__name__)


class CurrentProcess(object):
    """
    A non-posix process
    """
