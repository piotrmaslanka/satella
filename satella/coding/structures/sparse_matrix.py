import collections
import typing as tp

from satella.coding.recast_exceptions import silence_excs
from satella.coding.typing import T

KeyArg = tp.Tuple[tp.Union[int, slice], tp.Union[int, slice]]


def _cleanup_key(inst: tp.Union[int, slice], max_count: int):
    if isinstance(inst, slice):
        if not (inst.start is None and inst.stop is None and inst.step is None):
            raise IndexError('Custom slicing is not supported!')
        return Ellipsis
    elif isinstance(inst, int):
        if isinstance(inst, int):
            if inst < 0:
                inst += max_count
        return inst


class SparseMatrix(tp.Generic[T]):
    """
    A matrix of infinite size, that supports assignments.

    Set elements like this:

    >>> sm[1, 2] = 5
    >>> sm[:,1] = [5]
    >>> sm[1,:] = [5]
    >>> sm[:,:] = [[5]]

    where the first argument is the number of the column, counted from 0,
    and the second one is the number of the row, also counted from 0

    Note that custom slicing (ie. slices which are not :) will not be supported.
    Negative indices are supported.

    Undefined elements are considered to be of value None.

    Iterating over this matrix will yield it's consecutive rows.

    You can use the constructor in following way:

    >>> sm = SparseMatrix([[1, 2], [3, 4]])

    to construct a matrix that looks like

    ::

        |1 2|
        |3 4|
    """
    __slots__ = ('rows_dict', 'known_column_count', 'no_cols', 'no_rows')

    def max(self) -> T:
        """
        Return maximum element.

        None elements will be ignored.
        """
        item = self[0, 0]
        for row in self:
            for value in row:
                if value is None:
                    continue
                if value > item:
                    item = value
        return item

    def min(self) -> T:
        """
        Return minimum element.

        None elements will be ignored.
        """
        item = self[0, 0]
        for row in self:
            for value in row:
                if value is None:
                    continue

                if value < item:
                    item = value
        return item

    def __init__(self, matrix_data: tp.Optional[tp.List[tp.List[T]]] = None):
        self.rows_dict = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
        self.known_column_count = {}  # tp.Dict[int, int] column_no => amount
        self.no_cols = 0
        self.no_rows = 0
        if matrix_data:
            self[:, :] = matrix_data

    def get_neighbour_coordinates(self, col: int, row: int,
                                  include_diagonals: bool = True) -> tp.Iterator[
        tp.Tuple[int, int]]:
        """
        Return an iterator of coordinates to points neighbouring given point.
        :param col: column
        :param row: row
        :param include_diagonals: whether to include points having only a single point in common
        :return: an iterable of coordinates of neighbouring points. An iterator of tuple
            (col, row)
        """

        for delta_row in (-1, 0, 1):
            for delta_col in (-1, 0, 1):
                if not delta_row and not delta_col:
                    continue
                if abs(delta_col) + abs(delta_row) > 1:
                    if not include_diagonals:
                        continue
                cand_col = col + delta_col
                cand_row = row + delta_row
                if cand_col < 0 or cand_row < 0:
                    continue
                if cand_col >= self.no_cols or cand_row >= self.no_rows:
                    continue
                yield cand_col, cand_row

    def append_row(self, y: tp.Iterable[T]) -> None:
        """
        Append a row to the bottom of the matrix

        :param y: iterable with consequent columns
        """
        next_row = self.no_rows
        for col_no, z in enumerate(y):
            self[col_no, next_row] = z

    def clear(self) -> None:
        """
        Clear the contents of the sparse matrix
        """
        self.rows_dict = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
        self.known_column_count = {}  # tp.Dict[int, int] column_no => amount
        self.no_cols = 0
        self.no_rows = 0

    def __eq__(self, other: 'SparseMatrix') -> bool:
        return self.rows_dict == other.rows_dict

    def __bool__(self) -> bool:
        return self.no_rows == 0

    def _sanitize_key(self, key: KeyArg) -> KeyArg:
        col, row = key
        return _cleanup_key(col, self.no_cols), _cleanup_key(row, self.no_rows)

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

    def __iter__(self) -> tp.Iterator[tp.List]:
        return (self.get_row(i) for i in range(self.no_rows))

    def __len__(self) -> int:
        return self.no_rows

    def get_row(self, row_no: int) -> tp.List[T]:
        """
        Return a single row of provided number.

        The returned array has the same length as .columns

        :param row_no: row number, numbered from 0
        """
        if row_no not in self.rows_dict:  # check so as to avoid adding new entries
            return [None] * self.no_cols
        cols = self.rows_dict[row_no]
        output = []
        for i in range(self.no_cols):
            if i in cols:
                output.append(cols[i])
            else:
                output.append(None)
        return output

    def shoot(self) -> 'SparseMatrix':
        """
        Insert an empty cell between current cells. So the matrix which looked like
        [[1, 2], [3, 4]] will now look like [[1, None, 2], [None, None, None], [3, None, 4]]
        """
        new_sparse = SparseMatrix()
        for row_no, row in enumerate(self):
            for col_no, value in enumerate(row):
                new_sparse[col_no * 2, row_no * 2] = value
        return new_sparse

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

    def delete_row(self, row_no: int) -> None:
        """
        Delete a row with specified number

        :param row_no: number of the row to delete
        """
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

    def __getitem__(self,
                    item: KeyArg) -> tp.Union[tp.List[T], tp.List[tp.List[T]], T]:
        col, row = self._sanitize_key(item)

        if col is Ellipsis and row is Ellipsis:
            return list(self)
        elif col is Ellipsis:
            return [self[col_no, row] for col_no in range(self.no_cols)]
        elif row is Ellipsis:
            return [self[col, row_no] for row_no in range(self.no_rows)]
        else:
            if row >= self.no_rows:
                raise IndexError()
            elif col >= self.no_cols:
                raise IndexError()
            if row not in self.rows_dict:  # check so as to avoid adding new entries
                return None
            if col not in self.rows_dict[row]:
                return None
            return self.rows_dict[row][col]

    @silence_excs(TypeError, returns=0)
    def _calculate_column_count(self) -> int:
        return max(self.known_column_count) + 1

    @silence_excs(TypeError, returns=0)
    def _calculate_row_count(self) -> int:
        return max(self.rows_dict) + 1

    @silence_excs(KeyError)
    def __delitem__(self, key: KeyArg) -> None:
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

            if not self.rows_dict[row]:  # Have we got an empty row now?
                del self.rows_dict[row]

            self._decrement_column_count(col)

            self.no_cols = self._calculate_column_count()
            self.no_rows = self._calculate_row_count()
