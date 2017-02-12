# coding=UTF-8
"""
Allows you to preserve entire stack frame along with all variables (even pickles them).

After this, you can send this report somewhere. At target, it will be unpickled in a safe way
(without importing anything extra from environment). You can unpickle particular variables stored,
but that may involve an import.

Use in such a way:

    try:
        ...
    except WhateverError as e:
        tb = Traceback()
        print(tb.pretty_print())
        # you can now pickle it if you wish to
"""
import sys
import zlib
import six
import traceback
import inspect
try:
    import cPickle as pickle
except ImportError:
    import pickle


class ValuePicklingPolicy(object):
    """
    Default value pickling policy.

    For a "default" policy it's pretty customizable

    Override if need be, and pass the class (or instance) to Traceback
    """

    def __init__(self, enable_pickling=True, compress_at=128*1024):
        """
        :param enable_pickling: bool, whether to enable pickling at all
        :param compress_at: pickles longer than this (bytes) will be compressed
        """
        self.enable_pickling = enable_pickling
        self.compress_at = compress_at

    def should_pickle(self, value):
        """
        Should this value be pickled?

        :param value: value candidate
        :return: bool
        """
        return self.enable_pickling

    def should_compress(self, pickledata):
        """
        Should this pickle undergo compression?
        :param pickledata: bytes, pickle value
        :return: bool
        """
        return len(pickledata) > self.compress_at

    def get_compression_level(self, pickledata):
        """
        What compression level to use to pickle this?
        :param pickledata: bytes, pickle value
        :return: int, 1-9, where "1" is the fastest, and "9" is the slowest, but produces best compression
        """
        return 6


class StoredVariable(object):
    """
    Class used to store a variable value. Picklable.

    Attributes are:
        .repr - a text representation obtained using repr
        .typeinfo - a text representation of variable's type
        .pickle - bytes with pickled (optionally processed) value, or None if not available
        .pickle_type - what is stored in .pickle?
            None - nothing
            "pickle" - normal Python pickle
            "pickle/gzip" - Python pickle treated with zlib.compress
            "failed" - could not pickle, pickle contains a text with human-readable reason

    """
    __slots__ = ('repr', 'type_', 'pickle', 'pickle_type')

    def __init__(self, value, policy):
        """
        If value cannot be pickled, it's repr will be at least preserved

        :param value: any Python value to preserve
        :param policy: value pickling policy to use (instance)
        """
        self.repr = repr(value)
        self.type_ = repr(type(value))
        if six.PY2:
            self.repr = six.text_type(self.repr)
            self.type_ = six.text_type(self.type_)

        self.pickle = None
        self.pickle_type = None

        if policy.should_pickle(value):
            try:
                self.pickle = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
                self.pickle_type = 'pickle'
            except pickle.PicklingError as e:
                self.pickle = repr(e.args)
                self.pickle_type = "failed"
            else:
                if policy.should_compress(self.pickle):
                    try:
                        self.pickle = zlib.compress(self.pickle, policy.get_compression_level(self.pickle))
                        self.pickle_type = "pickle/gzip"
                    except zlib.error:
                        pass    # ok, keep normal

    def load_value(self):
        """
        Return the value that this represents.

        WARNING! This may result in importing things from environment, as pickle.loads will be called.

        :return: stored value - if picklable and was pickled
        :raises ValueError: value has failed to be pickled or was never pickled
        """
        if self.pickle_type is None:
            raise ValueError('value was never pickled')
        elif self.pickle_type == 'failed':
            raise ValueError('Value has failed to be pickled, reason is %s' % (self.pickle, ))
        elif self.pickle_type == 'pickle/gzip':
            pickle = zlib.decompress(self.pickle)
        elif self.pickle_type == 'pickle':
            pickle = self.pickle

        try:
            return pickle.loads(pickle)
        except pickle.UnpicklingError:
            raise ValueError('object picklable, but cannot load in this environment')


class StackFrame(object):
    """
    Class used to verily preserve stack frames. Picklable.
    """
    __slots__ = ('locals', 'globals', 'name', 'filename', 'lineno')

    def __init__(self, frame):
        """
        :type frame: Python stack frame
        """
        self.name = frame.f_code.co_name
        self.filename = frame.f_code.co_filename
        self.lineno = frame.f_lineno

        self.locals = {}
        for key, value in frame.f_locals.iteritems():
            self.locals[key] = StoredVariable(value)

        self.globals = {}
        for key, value in frame.f_globals.iteritems():
            self.globals[key] = StoredVariable(value)


class Traceback(object):
    """Class used to preserve exceptions. Picklable."""
    __slots__ = ('formatted_traceback', 'frames')

    def __init__(self, value_pickling_policy=ValuePicklingPolicy):
        """
        To be invoked while processing an exception is in progress

        :param value_pickling_policy: pickling policy for variables in stack frames.
                                      Can be a class (will be called with empty constructor), or instance
        """

        if inspect.isclass(value_pickling_policy):
            value_pickling_policy = value_pickling_policy()
        self.value_pickling_policy = value_pickling_policy

        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next

        self.frames = []
        f = tb.tb_frame
        while f:
            self.frames.append(StackFrame(f))
            f = f.f_back

        self.formatted_traceback = traceback.format_exc()

    def pickle(self):
        """Returns this instance, pickled"""
        return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

    def pretty_print(self):
        """
        Pretty-print the exception
        :return: unicode
        """
        k = []
        k.append(self.formatted_traceback)
        k.append(u'* Stack trace, innermost first')
        for frame in self.frames:
            k.append(u'** %s at %s:%s' % (frame.name, frame.filename, frame.lineno))
            for name, value in frame.locals.iteritems():
                try:
                    k.append(u'*** %s: %s' % (name, value.get_repr()))
                except:
                    k.append(u'*** %s: repr unavailable' % name)
        return u'\n'.join(k)