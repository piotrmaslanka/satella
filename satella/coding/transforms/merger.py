import typing as tp

from satella.coding.recast_exceptions import rethrow_as

from satella.coding.structures import SetHeap


class merge_series(tp.Iterator):
    """
    A merger for multiple sequences that return (timestamp, value).

    This will behave as a single-use iterator and return (timestamp, value1, value2, ...)
    """

    def __init__(self, *series: tp.Iterator[tp.Tuple[float, tp.Any]]):
        self.series = [iter(x) for x in series]
        try:
            self.next_preloaded_values = [next(x) for x in self.series]
        except StopIteration:
            self.empty = True
            return
        else:
            self.empty = False

        self.timestamps = SetHeap()
        timestamps = {x[0] for x in self.next_preloaded_values}
        max_ts = max(timestamps)
        self.timestamps.push(max_ts)

        self.super_next_preloaded_values = []
        for series in self.series:
            try:
                value = next(series)
                self.super_next_preloaded_values.append(value)
                self.timestamps.push(value[0])
            except StopIteration:
                self.super_next_preloaded_values.append(None)

    def __iter__(self) -> tp.Iterator:
        return self

    def advance(self, i: int) -> None:
        if self.super_next_preloaded_values[i] is None:
            raise RuntimeError('Cannot advance on series %s which is empty' % (i, ))
        else:
            self.next_preloaded_values[i] = self.super_next_preloaded_values[i]
            try:
                self.super_next_preloaded_values[i] = next(self.series[i])
                self.timestamps.push(self.super_next_preloaded_values[i][0])
            except StopIteration:
                self.super_next_preloaded_values[i] = None

    def next(self) -> None:
        minimum_timestamp, _ = min(self.next_preloaded_values)
        for i, v in enumerate(self.next_preloaded_values):
            if v[0] == minimum_timestamp:
                self.advance(i)

    def assert_preloaded(self, for_ts: int) -> bool:
        """
        Assert every next preloaded value can at least report for for_ts

        :param for_ts: timestamp to report for
        :return: whether every value can report for for_ts
        """
        for i, _ in enumerate(self.series):
            if self.super_next_preloaded_values[i] is None:
                if self.next_preloaded_values[i][0] > for_ts:
                    return False
            else:
                try:
                    while not (self.next_preloaded_values[i][0] <= for_ts < self.super_next_preloaded_values[i][0]):
                        self.advance(i)
                except TypeError:  # we've reached the finale
                    if self.next_preloaded_values[i][0] > for_ts:
                        return False
        return True

    def assert_have_timestamps(self) -> None:
        """
        Assert that self.timestamps is not empty, or raise StopIteration if it can't be filled in
        """
        if len(self.timestamps):
            return
        if all(map(lambda x: x is None, self.super_next_preloaded_values)):
            raise StopIteration('sequence exhausted')
        self.next()
        if not len(self.timestamps):
            raise StopIteration('cannot advance series anymore')

    @rethrow_as(IndexError, StopIteration)
    def __next__(self):
        if self.empty:
            raise StopIteration('empty right from the start')

        self.assert_have_timestamps()

        ts = self.timestamps.pop()

        while not self.assert_preloaded(ts):
            ts = self.timestamps.pop()  # throws IndexError

        output = (ts, *(v[1] for v in self.next_preloaded_values))
        return output
