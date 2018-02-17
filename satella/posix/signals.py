# coding=UTF-8
"""
Handle signals, like a boss
"""
from __future__ import print_function, absolute_import, division

import logging
import signal
import sys
import time

from satella.coding import typed

logger = logging.getLogger(__name__)

end = False

def __sighandler(a, b):
    global end
    end = True

@typed((list, None))
def hang_until_sig(extra_signals=None):
    """Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release."""
    extra_signals = extra_signals or []
    global end

    # Ascertain what Python are we working on. 2012 PyPy and earlier
    # may be affected by https://bugs.pypy.org/issue1255

    bugged_pypy = False
    try:
        import platform
    except ImportError:
        pass
    else:
        if platform.python_implementation() == 'PyPy':
            try:
                mon, day, year = platform.python_build()[1].split(' ')
                year = int(year)
            except (TypeError, ValueError):
                pass
            else:
                bugged_pypy = year <= 2012

    sleep = lambda: time.sleep(1) if bugged_pypy else signal.pause

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)

    while not end:
        try:
            sleep()
        except AttributeError:  # pause() is undefined on Windows
            try:  # we will sleep for small periods of time
                time.sleep(0.5)
            except IOError:  # "Interrupted system call"
                pass
