import signal
import sys
import types
import typing as tp

try:
    # noinspection PyProtectedMember
    SIG_TYPE = signal._SIG
except AttributeError:
    SIG_TYPE = int  # we are running on Windows


# noinspection PyUnusedLocal
def dump_frames_on(sig_no: tp.Optional[SIG_TYPE] = None,
                   stack_frame: tp.Optional[types.FrameType] = None,
                   output: tp.TextIO = sys.stderr):
    """
    Dump all stack frames of all threads including the values of all the local variables.

    :param sig_no: signal received. Default is None.
    :param stack_frame: Stack frame. Default is None.
    :param output: output to print to. Default is stderr
    :return:
    """
    from satella.instrumentation import Traceback

    output.write("Stack frame dump requested in response to signal %s\n" % (sig_no,))
    # noinspection PyProtectedMember
    for frame_no, frame in sys._current_frames().items():
        output.write("For stack frame %s" % (frame_no,))
        tb = Traceback(frame)
        tb.pretty_print(output=output)
    output.write("End of stack frame dump\n")


def install_dump_frames_on(signal_number: SIG_TYPE, output: tp.TextIO = sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal
    """
    signal.signal(signal_number,
                  lambda sig_no, stack_frame: dump_frames_on(sig_no, stack_frame, output))
