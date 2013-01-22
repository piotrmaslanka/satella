import cPickle as pickle
import sys
import traceback

class StoredVariable(object):
    __slots__ = ('can_repr', 'pickled', 'value')
    def __init__(self, value):
        self.can_repr = True
        try:
            self.pickled = True
            self.value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        except: # Object cannot be pickled for some reason
            self.pickled = False            
            try:
                self.value = repr(value)
            except: # __repr__ not available
                self.can_repr = False
                self.value = '*** repr not available ***'

    def get_repr_value(self):
        if not self.can_repr:
            raise ValueError, 'repr not available'
        if self.pickled:
            return __repr__(pickle.loads(self.value))
        else:
            return self.value

    def get_value(self):
        if not self.pickled:
            raise ValueError, 'object not picklable'
            # __repr__-representation is available though
        else:
            return pickle.loads(self.value)

class StackFrame(object):
    """
    Class used to verily preserve stack frames
    """
    __slots__ = ('locals', 'globals', 'name', 'filename')
    def __init__(self, frame):
        self.name = frame.f_code.co_name
        self.filename = frame.f_code.co_filename

        self.locals = {}
        for key, value in frame.f_locals.iteritems():
            self.locals[key] = StoredVariable(value)

        self.globals = {}
        for key, value in frame.f_globals.iteritems():
            self.globals[key] = StoredVariable(value)


class Trackback(object):
    """
    Class used to verily preserve exceptions.
    Picklable.
    """
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
