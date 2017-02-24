# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging

logger = logging.getLogger(__name__)


class Instrument(object):
    """Class used for generating metrics"""

    def __init__(self, name):
        self.name = name
        self.ancestry = name.split('.')

    def is_child_of(self, instrument):
        raise NotImplementedError