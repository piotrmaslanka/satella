import base64

try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle
import types
import typing as tp
import zlib

from satella.json import JSONAble


class GenerationPolicy:
    """
    A policy that manages generating a traceback

    For a "default" policy it's pretty customizable

    Override if need be, and pass the class (or instance) to Traceback

    :param enable_pickling: bool, whether to enable pickling at all
    :param compress_at: pickles longer than this (bytes) will be compressed
    :param repr_length_limit: maximum p_len of __repr__. None for no limit.
    :param compression_level: "1" is fastest, "9" is slowest
    """
    __slots__ = ('enable_pickling', 'compress_at', 'repr_length_limit', 'compression_level')

    def __init__(self, enable_pickling: bool = True,
                 compress_at: int = 128 * 1024,
                 repr_length_limit: int = 128 * 1024,
                 compression_level: int = 6):
        assert isinstance(compression_level, int) and 1 <= compression_level <= 9

        self.enable_pickling = enable_pickling  # type: bool
        self.compress_at = compress_at  # type: int
        self.repr_length_limit = repr_length_limit  # type: int
        self.compression_level = compression_level  # type: int

    def should_pickle(self, value: tp.Any) -> bool:
        """
        Should this value be pickled?

        :param value: value candidate
        :return: bool
        """
        return self.enable_pickling

    def should_compress(self, pickle_data: bytes) -> bool:
        """
        Should this pickle undergo compression?

        :param pickle_data: pickle value
        :return: bool
        """
        return len(pickle_data) > self.compress_at

    def get_compression_level(self, pickledata: bytes) -> int:
        """
        What compression level to use to pickle this?

        :param pickledata: bytes, pickle value
        :return: int, 1-9, where "1" is the fastest, and "9" is the slowest,
            but produces best compression
        """
        return self.compression_level

    def process_repr(self, r: str) -> str:
        """
        Process the string obtained from __repr__ing

        :param r: result of a __repr__ on value
        :return: processed result
        """
        if self.repr_length_limit is None:
            return r
        else:
            if len(r) > self.repr_length_limit:
                return r[:self.repr_length_limit] + u'...'
            else:
                return r


class StoredVariableValue(JSONAble):
    """
    Class used to store a variable value. Picklable.

    Attributes are:
        .repr - a text representation obtained using repr
        .typeinfo - a text representation of variable's type
        .pickle - bytes with pickled (optionally processed) value, or None if
            not available
        .pickle_type - what is stored in .pickle?
            None - nothing
            "pickle" - normal Python pickle
            "pickle/gzip" - Python pickle treated with zlib.compress
            "failed" - could not pickle, pickle contains a UTF-8 text with
                human-readable exception reason
            "failed/gzip" - compression failed, pickle contains a UTF-8 text with
                human-readable exception reason

    If value cannot be pickled, it's repr will be at least preserved.

    Note that the value itself won't be preserved.

    :param value: any Python value to preserve
    :param policy: policy to use (instance)
    """
    __slots__ = ('repr', 'type_', 'pickle', 'pickle_type')

    @classmethod
    def from_json(cls, x: dict) -> 'StoredVariableValue':
        sv = StoredVariableValue.__new__(StoredVariableValue)
        sv.repr = x['repr']
        sv.type_ = x['type']
        sv.pickle_type = x['pickle_type']
        if 'pickle' in x:
            sv.pickle = base64.b64decode(x['pickle'].encode('utf8'))
        sv.pickle = None
        return sv

    def to_json(self) -> dict:
        dct = {
            'repr': self.repr,
            'type': self.type_,
            'pickle_type': self.pickle_type
        }
        if self.pickle:
            dct['pickle'] = base64.b64encode(self.pickle).decode('utf8')
        return dct

    def __init__(self, value: tp.Any, policy: tp.Optional[GenerationPolicy] = None):
        self.repr = repr(value)  # type: str
        self.type_ = repr(type(value))  # type: str

        policy = policy or GenerationPolicy()

        self.repr = policy.process_repr(self.repr)

        self.pickle = None  # type: bytes
        self.pickle_type = None  # type: str

        if policy.should_pickle(value):
            try:
                self.pickle = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
                self.pickle_type = 'pickle'
            except BaseException as e:
                # yes, they all can happen!
                self.pickle = repr((e,) + e.args).encode('utf8')
                self.pickle_type = "failed"
            else:
                if policy.should_compress(self.pickle):
                    try:
                        self.pickle = zlib.compress(
                            self.pickle,
                            policy.get_compression_level(
                                self.pickle))
                        self.pickle_type = "pickle/gzip"
                    except zlib.error as e:
                        self.pickle = ('failed to gzip, reason is %s' % (repr(e),)).encode('utf8')
                        self.pickle_type = "failed/gzip"

    def load_value(self):
        """
        Return the value that this represents.

        WARNING! This may result in importing things from environment, as
        pickle.loads will be called.

        :return: stored value - if picklable and was pickled
        :raises ValueError: value has failed to be pickled or was never pickled
        """
        if self.pickle_type is None:
            raise ValueError('value was never pickled')
        elif self.pickle_type == 'failed':
            raise ValueError(
                'MemoryCondition has failed to be pickled, reason is %s' % (self.pickle,))
        elif self.pickle_type == 'pickle/gzip':
            pickle_ = zlib.decompress(self.pickle)
        elif self.pickle_type == 'pickle':
            pickle_ = self.pickle
        else:
            raise ValueError('unknown pickle type of %s' % (self.pickle_type,))

        try:
            return pickle.loads(pickle_)
        except pickle.UnpicklingError:
            raise ValueError(
                'object picklable, but cannot load in this environment')


class StackFrame(JSONAble):
    """
    Class used to verily preserve stack frames. Picklable.
    """
    __slots__ = ('locals', 'globals', 'name', 'filename', 'lineno')

    def __init__(self, frame: types.FrameType, policy: GenerationPolicy):
        self.name = frame.f_code.co_name  # type: str
        self.filename = frame.f_code.co_filename  # type: str
        self.lineno = frame.f_lineno  # type: int

        self.locals = {}  # type: tp.Dict[str, StoredVariableValue]
        for key, value in frame.f_locals.items():
            self.locals[key] = StoredVariableValue(value, policy)

        self.globals = {}  # type: tp.Dict[str, StoredVariableValue]
        for key, value in frame.f_globals.items():
            self.globals[key] = StoredVariableValue(value, policy)

    @classmethod
    def from_json(cls, x: dict) -> 'StackFrame':
        sv = StackFrame.__new__(StackFrame)
        sv.name = x['name']
        sv.filename = x['filename']
        sv.lineno = x['line_no'],
        sv.locals = {k: StoredVariableValue.from_json(v) for k, v in x['locals'].items()}
        sv.globals = {k: StoredVariableValue.from_json(v) for k, v in x['globals'].items()}
        return sv

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'filename': self.filename,
            'line_no': self.lineno,
            'locals': {k: v.to_json() for k, v in self.locals.items()},
            'globals': {k: v.to_json() for k, v in self.globals.items()}
        }
