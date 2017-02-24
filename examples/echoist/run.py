# coding=UTF-8
"""
It sounds like a melody
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import socket

logger = logging.getLogger(__name__)

from satella.posix import daemonize


if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 7))

    daemonize(uid='daemon', gid='daemon')
