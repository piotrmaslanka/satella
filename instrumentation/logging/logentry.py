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