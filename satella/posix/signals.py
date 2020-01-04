"""
Handle signals, like a boss
"""
import signal
import time

import typing as tp

end = False


def __sighandler(a, b):
    global end
    end = True


def hang_until_sig(extra_signals: tp.Optional[tp.List[int]] = None,
                   end_on_keyboard_interrupt: bool = True):
    """
    Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release.

    :param extra_signals: a list of extra signals to listen to
    :param end_on_keyboard_interrupt: whether to consider receiving a KeyboardInterrupt as
        a signal to finish
    """
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

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)

    while not end:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            if end_on_keyboard_interrupt:
                end = True

    end = False  # reset for next use
