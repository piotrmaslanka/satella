import logging
import typing
import threading


logger = logging.getLogger(__name__)


class LockedDataset(object):
    """
    A locked dataset. Subclass like

    class MyDataset(LockedDataset):
        def __init__(self):
            super(MyDataset, self).__init__()
            self.mydata: str = "lol wut"

    mds = MyDataset()
    with mds as md:
        md.mydata = "modified atomically"

    """

    def __init__(self):
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        return False

