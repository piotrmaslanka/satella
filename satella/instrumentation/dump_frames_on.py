import logging
import sys
import signal
from satella.instrumentation import Traceback


logger = logging.getLogger(__name__)


def dump_frames_on(sig_no, stack_frame, output):
    sys.stderr.write("Stack frame dump requested\n")
    # noinspection PyProtectedMember
    for frame in sys._current_frames():
        sys.stderr.write("For stack frame %s" % (repr(frame),))
        tb = Traceback(frame)
        tb.pretty_print(output=output)
    sys.stderr.write("End of stack frame dump\n")


def install_dump_frames_on(signal_number, output=sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal
    """
    signal.signal(signal_number, lambda sig_no, stack_frame: dump_frames_on(sig_no, stack_frame, output))
