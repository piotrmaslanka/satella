import gc
import signal
import sys
import typing as tp


def dump_memory_on(output: tp.TextIO = sys.stderr):
    """
    Dump statistics about current Python memory usage to target stream.

    Each Python object will be printed, along with a breakdown of most types and their total usage.

    Make sure you have enough memory to generate a breakdown. You can preallocate something at the
    start for example.

    .. warning:: This will return size of 0 on PyPy

    :param output: output, default is stderr
    """
    top_scores = {}
    instances = {}
    for obj in gc.get_objects():
        typ = type(obj)
        try:
            size = sys.getsizeof(obj)
        except TypeError:
            size = 0
        if typ in top_scores:
            top_scores[typ] += size
            instances[typ] += 1
        else:
            top_scores[typ] = size
            instances[typ] = 1
        output.write('object %s type %s size %s bytes\n' % (repr(obj), typ, size))

    output.write('----------------------------------\n')
    output.write('Memory usage scores: \n')
    output.write('----------------------------------\n')
    items = list(top_scores.items())
    items.sort(key=lambda y: -y[1])
    for typ, tot_size in items:
        output.write('%s: %s bytes %s instances\n' % (typ, tot_size, instances[typ]))


def install_dump_memory_on(signal_number, output: tp.TextIO = sys.stderr):
    """
    Instruct Python to dump all frames onto output, along with their local variables
    upon receiving given signal

    :param signal_number: number of the signal
    :param output: output
    """
    signal.signal(signal_number,
                  lambda sig_no, stack_frame: dump_memory_on(output))
