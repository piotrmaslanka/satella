# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import heapq

logger = logging.getLogger(__name__)





class TimeBasedHeap(object):
    """
    A heap of items sorted by timestamps.

    It is easy to ask for items, whose timestamps are LOWER than a value, and easy
    to remove them.

    Can be used to implement a scheduling service, ie. store jobs, and each interval query
    which of them should be executed. This loses time resolution, but is fast.

    #notthreadsafe
    """

    def __init__(self):
        """
        Initialize an empty heap
        """
        self.heap = []

    def put(self, timestamp, item):
        """
        Put an item of heap
        :param timestamp: timestamp for this item - float
        :param item: object
        """
        heapq.heappush(self.heap, (timestamp, item))

    def pop_less_than(self, timestamp):
        """
        Return a list of items with timestamps less than your value.

        Items will be removed from heap
        :return: list of tuple(timestamp::float, item)
        """
        out = []
        while len(self.heap) > 0:
            if self.heap[0][0] >= timestamp:
                return out
            out.append(heapq.heappop(self.heap))
        return out

    def remove(self, item):
        """
        Remove all things equal to item
        """
        self.heap = [q for q in self.heap if q != item]
        heapq.heapify(self.heap)

