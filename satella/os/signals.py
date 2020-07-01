import signal
from satella.time import sleep
import typing as tp

end = False


def __sighandler(a, b):
    global end
    end = True


def hang_until_sig(extra_signals: tp.Optional[tp.Sequence[int]] = None) -> None:
    """
    Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release.

    :param extra_signals: a list of extra signals to listen to
    """
    global end
    extra_signals = extra_signals or ()

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)

    while not end:
        sleep(0.5, True)

    end = False  # reset for next use
