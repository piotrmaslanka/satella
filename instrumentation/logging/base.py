import time

class LogEntry(object):
    """Class that represents a single log entry in the system"""
    def __init__(self, who, tags, when=None):
        """
        @param who: Name of the logging service. System components in granularity-descending
            hierarchy should be separated with dots, eg. "http.network.accept"
        @type who: str
        @param tags: a sequence of str or a str (space-separated) of tags that can be used to
            machine-process the sequence set
        @param when: optional, UTC timestamp of time that event happened
        @type when: int or long
        """
        if when == None: when = time.time()

        self.when = when    #: UTC timestamp of the event
        self.who = who      #: service that logged. Hierarchy separated by dotch

        if isinstance(tags, str):
            self.tags = set(tags.split(' '))
        else:
            self.tags = set(tags)

        self.attachments = []   #: list of pair (attachment name, picklable attachment object)

    def attach(self, *args):
        """
        Attaches a piece of data to the log entry.
        Invoke with either one argument (will attach the data without a name) or two arguments
        (first of them will be a str, name of the entry, second one - the data to attach)
        """
        if len(args) == 1:  # Attach an attachment without a name
            self.attachments.append((None, args[0]))
        elif len(args) == 2: # Attach a named attachment
            self.attachments.append(args)
        else:
            raise ValueError, 'more than 2 arguments'

        return self

class LogSet(object):
    """
    A sequence of .when-ordered log events along with methods to process the stream.

    You may extend that to cater for your own peculiar logging stuff
    """
    def __init__(self, events=[]):
        self.events = events    #: list of LogEntry

    def count(self):
        """Return the number of log entries in this set"""
        return len(self.events)

    def filter_when_from(self, dt):
        """
        Returns the subset of this event set where .when is more or equal to dt
        @type dt: int or long
        """
        return LogSet([x for x in self.events if x.when >= dt])        

    def filter_when_to(self, dt):
        """
        Returns the subset of this event set where .when is less or equal to dt
        @type dt: int or long
        """
        return LogSet([x for x in self.events if x.when <= dt])        

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

        return LogSet([x for x in self.events if tag.issubset(x.tags)])

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
        for evt in (x for x in self.events if x.who.startswith(hstart)):
            if len(evt.who) == f:
                n.append(evt)
            elif evt.who[f] == '.':
                n.append(evt)
        return LogSet(n)