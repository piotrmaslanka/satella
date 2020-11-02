import collections


class RollingArithmeticAverage:
    """
    A class to implement a rolling arithmetic average over n last entries

    :param n: amount of last entries to count
    """
    __slots__ = ('n', 'queue', 'tot_sum')

    def __init__(self, n: int = 100):
        self.n = n
        self.queue = collections.deque()
        self.tot_sum = 0

    def insert(self, x: float) -> None:
        """
        Add a value to the rolling average, discarding the previous entry if the
        buffer size is exceeded

        :param x: sample to insert
        """
        if len(self.queue) >= self.n:
            prev_entry = self.queue.popleft()
            self.tot_sum -= prev_entry

        self.queue.append(x)
        self.tot_sum += x

    def avg(self) -> float:
        """
        Compute current average

        :return: current average
        :raises ZeroDivisionError: the average buffer is empty
        """
        return self.tot_sum / len(self.queue)

    def clear(self) -> None:
        """
        Clear the rolling average buffer
        """
        self.queue.clear()
        self.tot_sum = 0
