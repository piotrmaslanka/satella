import collections
import itertools
import typing as tp

from satella.coding.recast_exceptions import silence_excs
from .dictionaries import SelfCleaningDefaultDict
T = tp.TypeVar('T')


class SparseMatrix(tp.Generic[T]):
    """
    A matrix of infinite size, that supports assignments.

    Set elements like this:

    >>> sm[1, 2]

    where the first argument is the number of the column, counted from 0,
    and the second one is the number of the row, also counted from 0

    Undefined elements are considered to be of value None
    """
    def __init__(self):
        self.rows_dict = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
        self.known_column_count = {}        # tp.Dict[int, int] column_no => amount
        self.no_cols = 0
        self.no_rows = 0

    @property
    def columns(self) -> int:
        """Return the amount of columns"""
        return self.no_cols

    @property
    def rows(self) -> int:
        """Return the amount of rows"""
        return self.no_rows

    def get_rows(self) -> tp.Iterator[tp.List[T]]:
        """
        Return an iterator that yields consecutive rows of the matrix
        """
        return (self.get_row(i) for i in range(self.no_rows))

    def __iter__(self) -> tp.Iterator[tp.List]:
        return self.get_rows()

    def __len__(self) -> int:
        return self.no_rows

    def get_row(self, row_no: int) -> tp.List[T]:
        """
        Return a single row of provided number.

        The returned array has the same length as .columns

        :param row_no: row number, numbered from 0
        """
        if row_no not in self.rows_dict:     # check so as to avoid adding new entries
            return [None]*self.no_cols
        cols = self.rows_dict[row_no]
        output = []
        for i in range(self.no_cols):
            if i in cols:
                output.append(cols[i])
            else:
                output.append(None)
        return output

    def _increment_column_count(self, col_no: int) -> None:
        if col_no not in self.known_column_count:
            self.known_column_count[col_no] = 1
        else:
            self.known_column_count[col_no] += 1

    def _decrement_column_count(self, col_no: int) -> None:
        if self.known_column_count[col_no] == 1:
            del self.known_column_count[col_no]
        else:
            self.known_column_count[col_no] -= 1

    def __setitem__(self, key: tp.Tuple[int, int], value: T):
        col, row = key
        if col > self.no_cols-1:
            self.no_cols = col + 1
        if row > self.no_rows-1:
            self.no_rows = row + 1

        if row not in self.rows_dict:
            self._increment_column_count(col)
        elif col not in self.rows_dict[row]:
            self._increment_column_count(col)
        self.rows_dict[row][col] = value

    def __getitem__(self, item: tp.Tuple[int, int]) -> tp.Optional[T]:
        col, row = item
        if row not in self.rows_dict:    # check so as to avoid adding new entries
            return None
        if col not in self.rows_dict[row]:
            return None
        return self.rows_dict[row][col]

    @silence_excs(KeyError)
    def __delitem__(self, key: tp.Tuple[int, int]) -> None:
        col, row = key
        del self.rows_dict[row][col]
        if not self.rows_dict[row]:
            del self.rows_dict[row]

        self._decrement_column_count(col)

        try:
            self.no_cols = max(self.known_column_count)+1
        except TypeError:
            self.no_cols = 0
        try:
            self.no_rows = max(self.rows_dict) + 1
        except TypeError:
            self.no_rows = 0
