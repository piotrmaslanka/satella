# coding=UTF-8
"""
Handle signals, like a boss
"""
from __future__ import print_function, absolute_import, division
import six
import signal
import logging
from threading import Lock
from satella.coding import typed

logger = logging.getLogger(__name__)


@typed(list)
def hang_until_sig(extra_signals=[]):
    """Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release."""
    me_lock = Lock()
    me_lock.acquire()

    def insignum(sig):
        def o(sigq, frame):
            if sig != sigq:
                logger.warning('Handler for signal %s responded for signal %s', sig, sigq)
            else:
                logger.warning('Received signal %s', sigq)
                me_lock.release()
        return o

    for s in extra_signals + [signal.SIGTERM, signal.SIGINT]:
        signal.signal(s, insignum(s))

    while True:
        try:
            me_lock.acquire()
        except KeyboardInterrupt:
            pass
