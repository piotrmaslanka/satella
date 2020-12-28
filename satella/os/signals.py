import signal
import typing as tp

from satella.time import sleep

end = False


def __sighandler(a, b):
    global end
    end = True


def hang_until_sig(extra_signals: tp.Optional[tp.Sequence[int]] = None,
                   sleep_interval: float = 2) -> None:
    """
    Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release.

    Periodic sleeping with polling was chosen as the approach of choice, as pause() seemed
    to work a bit shakily multi-platform.

    :param extra_signals: a list of extra signals to listen to
    :param sleep_interval: amount of time to sleep between checking for termination condition.
    """
    global end
    extra_signals = extra_signals or ()

    old_term = signal.getsignal(signal.SIGTERM)
    old_int = signal.getsignal(signal.SIGINT)
    olds = []

    # Set the signal handler
    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        olds.append(signal.getsignal(s))
        signal.signal(s, __sighandler)

    while not end:
        sleep(sleep_interval, True)

    # Unset the signal handler
    signal.signal(signal.SIGTERM, old_term)
    signal.signal(signal.SIGINT, old_int)
    for s, old_handler in zip(extra_signals, olds):
        signal.signal(s, old_handler)

    end = False  # reset for next use
