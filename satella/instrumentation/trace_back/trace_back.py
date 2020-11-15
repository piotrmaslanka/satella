import inspect
import io

try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle
import sys
import traceback
import types
import typing as tp

from satella.json import JSONAble
from .classes import StackFrame, GenerationPolicy


def frame_from_traceback(tb: types.TracebackType) -> types.FrameType:
    """
    Extract the bottom stack frame from a traceback

    :param tb: traceback to extract the frame
    :return: bottom stack frame
    """
    while tb.tb_next:
        tb = tb.tb_next
    return tb.tb_frame


class Traceback(JSONAble):
    """
    Class used to preserve exceptions and chains of stack frames.
     Picklable.

    If starting frame is not given, an exception must be in progress.

    You can also convert it to a secure representation, ie. one that will be completely JSON
    and thus safe to load from untrusted sources. You will not lose the unpicklability of them by doing
    so, as they can be safely reconstructed (pickle will be encoded as base64 string).

    :param starting_frame: frame to start tracking the traceback from.
        Must be either None, in which case an exception must be in progress and will be taken
        else must be an instance of <class 'frame'>.
    :param policy: policy for traceback generation
    :raise ValueError: there is no traceback to get info from!
        Is any exception in process?
     """
    __slots__ = ('formatted_traceback', 'frames')

    def __str__(self) -> str:
        out = ['Traceback:\n']
        for frame in self.frames:
            out.append(str(frame))
        return ''.join(out)

    def __init__(self, starting_frame: tp.Optional[types.FrameType] = None,
                 policy=GenerationPolicy):
        if inspect.isclass(policy):
            value_pickling_policy = policy()
        else:
            value_pickling_policy = policy

        self.frames = []  # type: tp.List[StackFrame]

        if starting_frame is None:
            tb = sys.exc_info()[2]
            if tb is not None:
                f = frame_from_traceback(tb)
            else:
                f = inspect.currentframe()
        else:
            f = starting_frame

        while f:
            self.frames.append(StackFrame(f, value_pickling_policy))
            f = f.f_back

        self.formatted_traceback = str(traceback.format_exc())

    def __eq__(self, other: 'Traceback') -> bool:
        return self.frames == other.frames

    def pickle_to(self, stream: tp.BinaryIO) -> None:
        """Pickle self to target stream"""
        pickle.dump(self, stream, pickle.HIGHEST_PROTOCOL)

    def pickle(self) -> bytes:
        """Returns this instance, pickled"""
        bio = io.BytesIO()
        self.pickle_to(bio)
        return bio.getvalue()

    @classmethod
    def from_pickle(cls, pick: tp.Union[io.BytesIO, bytes]) -> 'Traceback':
        """
        Load a traceback from a pickle

        :param pick: either bytes or a BytesIO to load it from
        :return: previously serialized Traceback
        :raises ValueError: unserialized object is not a Traceback!
        """
        if isinstance(pick, io.BytesIO):
            a = pickle.load(pick)
        else:
            a = pickle.loads(pick)
        if not isinstance(a, Traceback):
            raise ValueError('%s is not a traceback!' % (type(a),))
        return a

    def to_json(self) -> dict:
        return {
            'frames': [frame.to_json() for frame in self.frames],
            'formatted_traceback': self.formatted_traceback
        }

    @classmethod
    def from_json(cls, x: dict) -> 'Traceback':
        tb = Traceback.__new__(Traceback)
        tb.frames = [StackFrame.from_json(y) for y in x['frames']]
        tb.formatted_traceback = x['formatted_traceback']
        return tb

    def pretty_format(self) -> str:
        """
        Return a multi-line, pretty-printed representation of all exception
        data.

        :return: text
        """
        bio = io.StringIO()
        self.pretty_print(bio)
        return bio.getvalue()

    def pretty_print(self, output: tp.TextIO = sys.stderr) -> None:
        """
        Pretty-print the exception

        :param output: a file-like object in text mode
        :return: unicode
        """
        output.write(self.formatted_traceback)
        output.write(u'\n* Stack trace, innermost first\n')
        for frame in self.frames:
            output.write(u'** %s at %s:%s\n' % (frame.name, frame.filename, frame.lineno))
            for name, value in frame.locals.items():
                try:
                    output.write(u'*** %s: %s\n' % (name, value.repr))
                except BaseException as e:
                    output.write(
                        u'*** %s: repr unavailable (due to locally raised %s)\n' % (name, repr(e)))
