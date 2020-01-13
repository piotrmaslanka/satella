import logging
import signal
import sys
import types
import typing as tp

try:
    SIG_TYPE = signal._SIG
except AttributeError:
    SIG_TYPE = int  # we are running on Windows

logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
# noinspection PyProtectedMember
def dump_frames_on(sig_no: SIG_TYPE, stack_frame: types.FrameType, output: tp.TextIO):
    from satella.instrumentation import Traceback

    sys.stderr.write("Stack frame dump requested\n")
    # noinspection PyProtectedMember
    for frame_no, frame in sys._current_frames().items():
        sys.stderr.write("For stack frame %s" % (frame_no,))
        tb = Traceback(frame)
        tb.pretty_print(output=output)
    sys.stderr.write("End of stack frame dump\n")


# noinspection PyProtectedMember
def install_dump_frames_on(signal_number: SIG_TYPE, output: tp.TextIO = sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal
    """
    signal.signal(signal_number,
                  lambda sig_no, stack_frame: dump_frames_on(sig_no, stack_frame, output))
