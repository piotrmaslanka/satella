import time
import json
import cPickle as pickle
import base64

class LogEntry(object):
    """
    Class that represents a single log entry in the system.

    Basic log has at least a timestamp, information who logged the event, a set of 
    tags that designate severity or classification. A log entry can also have a 'main
    attachment', which can be a number, string, sequence of those objects or a dictionary
    of those objects. Main attachment serves as additional source of information that
    can be deployed for indexing the log entries.

    A log entry can additionally have one or more named attachments. There can be at 
    most one attachment with given name. Those are serializes and are not expected to be
    indexable during log retrieval. 
    """
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

        self.attachments = {}  #: dict(attachment name::str => attachment)
        self.main_attachment = None #: main attachment

    def attach(self, *args):
        """
        Attaches a piece of data to the log entry.
        Invoke with either one argument (will attach the data as main attachment) or two arguments
        (first of them will be a str, name of the entry, second one - the data to attach).
        """
        if len(args) == 1:  # Attach an attachment without a name
            self.main_attachment = args[0]
        elif len(args) == 2: # Attach a named attachment
            self.attachments[args[0]] = args[1]
        else:
            raise ValueError, 'more than 2 arguments'

        return self


    def to_compact(self):
        """Serializes this as Python-specific string"""
        return pickle.dumps(
                (self.when, self.who, self.tags, self.main_attachment, self.attachments),
                pickle.HIGHEST_PROTOCOL
            )

    @staticmethod
    def from_compact(p):
        """@param p: str"""
        when, who, tags, main_attachment, attachments = pickle.loads(p)
        le = LogEntry(who, tags, when).attach(main_attachment)
        for k, v in attachments.iteritems():
            le.attach(k, v)
        return le

    def to_JSON(self):
        """Serializes this object to JSON."""
        return json.dumps({
                'when': self.when,
                'who': self.who,
                'tags': sorted(self.tags),
                'main': self.main_attachment,
                'attachments': dict((
                            (name, base64.b64encode(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)))
                            for name, value in self.attachments.iteritems()
                        ))
            })

    @staticmethod
    def from_JSON(jsonstr):
        """Unserializes this object from JSON. This may be potentially
        unsafe, as we are unpickling Python objects.

        Know that main_attachment's str's will get converted to Unicode, due to how JSON works.
        @type jsonstr: str"""
        jo = json.loads(jsonstr)
        le = LogEntry(str(jo['who']), map(str, jo['tags']), jo['when']).attach(jo['main'])
        for aname, avs in jo['attachments'].iteritems():
            le.attach(aname, pickle.loads(base64.b64decode(avs)))
        return le
