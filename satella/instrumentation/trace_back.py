# coding=UTF-8
"""
Allows you to preserve entire stack frame along with all variables (even pickles them).

Use in such a way:

    try:
        ...
    except WhateverError as e:
        tb = Traceback()
        print(tb.pretty_print())
        # you can now pickle it if you wish to
"""
import sys
import six
import traceback
try:
    import cPickle as pickle
except ImportError:
    import pickle


class StoredVariable(object):
    """Class used to store a variable value. Picklable."""
    __slots__ = ('repr', 'pickle')

    def __init__(self, value):
        """
        If value cannot be pickled, it's repr will be at least preserved

        :param value: any Python value to preserve
        """
        self.repr = repr(value)
        if six.PY2:
            self.repr = six.text_type(self.repr)

        try:
            self.pickle = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError:
            self.pickle = None 

    def get_repr(self):
        """
        Return a representation of the value
        :return:
        """
        return self.repr

    def get_value(self):
        """
        Return the value that this represents.
        :return: stored value - if unpicklable
        :raises ValueError: unable to unpickle
        """
        if self.pickle is None:
            raise ValueError('object not picklable')
        else:
            try:
                return pickle.loads(self.pickle)
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

    def __init__(self):
        """To be invoked while processing an exception is in progress"""

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