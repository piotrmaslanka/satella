import logging
import typing as tp
import sys
logger = logging.getLogger(__name__)
from satella.instrumentation import Traceback


def install_dump_frames_on(signal, output=sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal
    """
    def dump_frames_on(sig_no, stack_frame):

        sys.stderr.write("Stack frame dump requested\n")
        for frame in sys._current_frames():
            sys.stderr.write("For stack frame %s" % (repr(frame), ))
            tb = Traceback(frame)
            tb.pretty_print(output=sys.stderr)
    signal.signal(signal, dump_frames_on)
