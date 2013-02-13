import time
import json
import cPickle as pickle
import base64

class LogEntry(object):
    """
    Class that represents a single log entry in the system.

    Basic log has at least a timestamp, information who logged the event, a set of 
    tags that designate severity or classification. A log entry can also have extra data,
    essentially a dictionary accessable for read as if it were part of this object 
    (via __getattr__). Main attachment serves as additional source of information that
    can be deployed for indexing the log entries.

    A log entry can additionally have one or more named attachments. There can be at 
    most one attachment with given name. Those are serialized and are not expected to be
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
        self.data = {} #: extra data

    def set_data(self, **kwargs):
        self.data.update(kwargs)
        return self

    def __getattr__(self, aname):
        return self.data[aname]

    def attach(self, key, value):
        """
        Attaches a piece of data to the log entry.
        @param key: name of the piece of data
        @type key: str
        @param value: picklable value to store
        """
        self.attachments[key] = value
        return self

    def to_compact(self):
        """Serializes this as Python-specific string"""
        return pickle.dumps(
                (self.when, self.who, self.tags, self.data, self.attachments),
                pickle.HIGHEST_PROTOCOL
            )

    @staticmethod
    def from_compact(p):
        """@param p: str"""
        when, who, tags, data, attachments = pickle.loads(p)
        le = LogEntry(who, tags, when).set_data(**data)
        for k, v in attachments.iteritems():
            le.attach(k, v)
        return le

    def to_JSON(self):
        """Serializes this object to JSON."""
        return json.dumps({
                'when': self.when,
                'who': self.who,
                'tags': sorted(self.tags),
                'data': self.data,
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
        le = LogEntry(str(jo['who']), map(str, jo['tags']), jo['when']).set_data(**jo['data'])
        for aname, avs in jo['attachments'].iteritems():
            le.attach(aname, pickle.loads(base64.b64decode(avs)))
        return le
