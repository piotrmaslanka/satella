import collections
import typing as tp

from satella.coding.recast_exceptions import silence_excs
T = tp.TypeVar('T')
KeyArg = tp.Tuple[tp.Union[int, slice],
                  tp.Union[int, slice]]


class SparseMatrix(tp.Generic[T]):
    """
    A matrix of infinite size, that supports assignments.

    Set elements like this:

    >>> sm[1, 2] = 5
    >>> sm[...,1] = [5]
    >>> sm[1,...] = [5]
    >>> sm[...,...] = [[5]]
    >>> sm[:,1] = [5]
    >>> sm[1,:] = [5]
    >>> sm[:,:] = [[5]]

    where the first argument is the number of the column, counted from 0,
    and the second one is the number of the row, also counted from 0

    Note that custom slicing (ie. slices which are not :) are not yet supported.
    Negative indices are supported.
    # todo add custom slicing

    Undefined elements are considered to be of value None.
    """
    def __init__(self):
        self.rows_dict = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
        self.known_column_count = {}        # tp.Dict[int, int] column_no => amount
        self.no_cols = 0
        self.no_rows = 0

    def clear(self) -> None:
        """
        Clear the contents of the sparse matrix
        """
        self.rows_dict = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
        self.known_column_count = {}        # tp.Dict[int, int] column_no => amount
        self.no_cols = 0
        self.no_rows = 0

    def __eq__(self, other: 'SparseMatrix') -> bool:
        return self.rows_dict == other.rows_dict

    def __bool__(self) -> bool:
        return self.no_rows == 0

    def _sanitize_key(self, key: KeyArg) -> KeyArg:
        col, row = key

        if isinstance(col, slice):
            assert col.start is None and col.stop is None and col.step is None, \
                'Custom slicing not supported yet!'
            col = Ellipsis
        elif isinstance(col, int):
            if col < 0:
                col += self.no_cols
        if isinstance(row, slice):
            assert row.start is None and row.stop is None and row.step is None, \
                'Custom slicing not supported yet!'
            row = Ellipsis
        elif isinstance(row, int):
            if row < 0:
                row += self.no_rows

        return col, row

    @classmethod
    def from_iterable(cls, y: tp.Iterable[tp.Iterable[T]]):
        """
        Construct a sparse matrix given a row-first iterable. That iterable must
        return another iterable, that will yield values for given column.

        :param y: an iterable describing the sparse matrix
        :return: a sparse matrix object
        """
        sm = SparseMatrix()
        for row_no, cols in enumerate(y):
            for col_no, value in enumerate(cols):
                sm[col_no, row_no] = value
        return sm

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

    def _delete_row(self, row_no: int) -> None:
        cols = list(self.rows_dict[row_no].keys())  # Copy it here
        for col_no in cols:
            del self[col_no, row_no]

    def __setitem__(self, key: KeyArg,
                    value: tp.Union[tp.Iterable[T], T]) -> None:
        """
        Use this to update either a single piece of the matrix, or entire row.

        Use like:

        >>> sm[1, 2] = 5
        >>> sm[...,1] = [5]
        >>> sm[1,...] = [5]
        >>> sm[...,...] = [[5]]
        >>> sm[:,1] = [5]
        >>> sm[1,:] = [5]
        >>> sm[:,:] = [[5]]

        Note that setting an element to None is the same as deleting it.
        """
        if value is None:
            del self[key]
            return

        col, row = self._sanitize_key(key)

        if col is Ellipsis and row is Ellipsis:
            sm = SparseMatrix.from_iterable(value)
            self.rows_dict = sm.rows_dict
            self.no_rows = sm.no_rows
            self.no_cols = sm.no_cols
            self.known_column_count = sm.known_column_count
        elif col is Ellipsis:
            for col_no, val in enumerate(value):
                self[col_no, row] = val
        elif row is Ellipsis:
            for row_no, val in enumerate(value):
                self[col, row_no] = val
        else:
            if col >= self.no_cols:
                self.no_cols = col + 1
            if row >= self.no_rows:
                self.no_rows = row + 1

            if row not in self.rows_dict:
                self._increment_column_count(col)
            elif col not in self.rows_dict[row]:
                self._increment_column_count(col)
            self.rows_dict[row][col] = value

    def __getitem__(self, item: tp.Tuple[int, int]) -> tp.Optional[T]:
        col, row = self._sanitize_key(item)

        if col is Ellipsis and row is Ellipsis:
            return list(self)
        elif col is Ellipsis:
            lst = [None] * self.no_cols
            for col_no in range(self.no_cols):
                lst[col_no] = self[col_no, row]
            return lst
        elif row is Ellipsis:
            lst = [None] * self.no_rows
            for row_no in range(self.no_rows):
                lst[row_no] = self[col, row_no]
            return lst
        else:
            if row not in self.rows_dict:    # check so as to avoid adding new entries
                return None
            if col not in self.rows_dict[row]:
                return None
            return self.rows_dict[row][col]

    @silence_excs(TypeError, returns=0)
    def _calculate_column_count(self):
        return max(self.known_column_count)+1

    @silence_excs(TypeError, returns=0)
    def _calculate_row_count(self):
        return max(self.rows_dict) + 1

    @silence_excs(KeyError)
    def __delitem__(self, key: tp.Tuple[int, int]) -> None:
        col, row = self._sanitize_key(key)

        if row is Ellipsis and col is Ellipsis:
            self.clear()
        elif col is Ellipsis:
            for col_no in range(self.no_cols):
                del self[col_no, row]
        elif row is Ellipsis:
            for row_no in range(self.no_rows):
                del self[col, row_no]
        else:
            # Check if the element is there
            if row not in self.rows_dict:
                return
            if col not in self.rows_dict[row]:
                return

            del self.rows_dict[row][col]

            if not self.rows_dict[row]:     # Have we got an empty row now?
                del self.rows_dict[row]

            self._decrement_column_count(col)

            self.no_cols = self._calculate_column_count()
            self.no_rows = self._calculate_row_count()
