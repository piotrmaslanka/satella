import cPickle as pickle
import sys
import traceback

class StoredVariable(object):
    __slots__ = ('repr', 'pickle')
    def __init__(self, value):
        try:
            self.repr = repr(value)
        except:
            self.repr = None

        try:
            self.pickle = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        except:
            self.pickle = None 

    def get_repr(self):
        if self.repr == None:
            raise ValueError, 'repr not available'
        else:
            return self.repr

    def get_value(self):
        if self.pickle == None:
            raise ValueError, 'object not picklable'
        else:
            return pickle.loads(self.pickle)

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
