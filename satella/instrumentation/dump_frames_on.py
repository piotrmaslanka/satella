import logging
import sys
from satella.instrumentation import Traceback


logger = logging.getLogger(__name__)


def install_dump_frames_on(signal, output=sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal
    """
    def dump_frames_on(sig_no, stack_frame):
        sys.stderr.write("Stack frame dump requested\n")
        # noinspection PyProtectedMember
        for frame in sys._current_frames():
            sys.stderr.write(f"For stack frame %s" % (repr(frame), ))
            tb = Traceback(frame)
            tb.pretty_print(output=output)
        sys.stderr.write("End of stack frame dump\n")
    signal.signal(signal, dump_frames_on)
