class LoggerInterface(object):
    """Interface for logger classes"""

    def specialize(self, **kwargs):
        """
        Return a new class with logger interface.
        The child class will log all events to parent
        logger, save for the fact that each entry will
        have something modified, depending on kwargs:

        If there is key:
        - tag=value :   child will append value to tags. Will
            append multiple values if value is a sequence
        - who=value:  child will prepend the who hierarchy
            intelligently, ie. if primary hierarchy is empty
            no dot will be added
        """
        return SpecializedLoggerObject(self, **kwargs)

    def produce_entry(self, *args, **kwargs):
        """The helper to .log() that outputs a LogEntry
        object from parameters"""
        raise RuntimeError, 'abstract'

    def log_entry(self, entry):
        """Relays L{LogEntry} entry to logging backend"""
        raise RuntimeError, 'abstract'

    def log(self, *args, **kwargs):
        """
        Invoke appropriate LogEntry constructor with 
        *args and **kwargs. How this is parsed is totally
        dependent on the implementation - make it so that
        actually it with your program is simple.

        Relay the log onto suitable logging backend.

        This is a convenience method.
        """
        self.log_entry(self.produce_entry(*args, **kwargs))

class SpecializedLoggerObject(LoggerInterface):
    """A helper object that can have specializations delegated"""
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.kwargs = kwargs

    def produce_entry(self, *args, **kwargs):
        e = self.parent.produce_entry(*args, **kwargs)
        if 'tag' in self.kwargs:
            if isinstance(self.kwargs['tag'], str):
                e.tags = e.tags + (self.kwargs['tag'], )
            else:
                e.tags = e.tags + self.kwargs['tag']
        if 'who' in self.kwargs:
            if e.who == '':
                e.who = self.kwargs['who']
            else:
                e.who = '%s.%s' % (e.who, self.kwargs['who'])

        return e
