class LogSet(object):
    """
    A sequence of .when-ordered log events along with methods to process the stream.

    You may extend that to cater for your own peculiar logging stuff. You may even
    override it if you have a storage backend and it would be more efficient to do 
    so without loading the entire thing into memory.
    """
    def __init__(self, events=[]):
        self._events = events    #: list of LogEntry

    def count(self):
        """
        Return the number of log entries in this set.
        Do not expect that this call will be always available, because on some backends
        it would be just infeasible. If you are overriding this class, feel free not
        to implement .count()
        """
        return len(self._events)

    def events(self):
        """
        Return an iterator that will return events sorted ascending 
        order by .when, and that will return L{LogEntry} objects (or 
        descendants)
        """
        return iter(self._events)

    def filter_when_from(self, dt):
        """
        Returns the subset of this event set where .when is more or equal to dt
        @type dt: int or long
        """
        return LogSet([x for x in self._events if x.when >= dt])        

    def filter_when_to(self, dt):
        """
        Returns the subset of this event set where .when is less or equal to dt
        @type dt: int or long
        """
        return LogSet([x for x in self._events if x.when <= dt])        

    def filter_tag(self, tag):
        """
        Returns the subset of this event set where tag occurs.
        @param tag: Tag (or sequence of tags) that is supposed to occur in each of the returned entries
        @type tag: str or sequence
        @return: L{LogSet} with entries
        """
        if isinstance(tag, str):
            tag = set((tag, ))
        else:
            tag = set(tag)

        return LogSet([x for x in self._events if tag.issubset(x.tags)])

    def filter_hierarchy(self, hstart):
        """
        Returns the subset of this event set where hstart is the start of
        logger hierarchy.

        Eg. if we have events:
            satella.instrumentation.test
            satella.instrumentation
            satella.instrumentationes
            satella.helloworld

        And we call .filter_hierarchy('satella.instrumentation') we'll receive only TWO
        first results

        @param hstart: String that hierarchy is supposed to start from
        @type tag: str
        @return: L{LogSet} with entries
        """
        f = len(hstart)
        n = []
        for evt in (x for x in self._events if x.who.startswith(hstart)):
            if len(evt.who) == f:
                n.append(evt)
            elif evt.who[f] == '.':
                n.append(evt)
        return LogSet(n)