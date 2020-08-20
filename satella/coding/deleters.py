import copy
import typing as tp
import collections

ITER_KEYS = 0
ITER_VALUES = 1
ITER_ITEMS = 2
T = tp.TypeVar('T')


class DictDeleter:
    """
    Having problems deleting entries from your dict while iterating on them? No problem. Just swap
    the following:

    >>> keys_to_delete = []
    >>> for key, value in my_dict.items():
    >>>     if value.should_delete():
    >>>         keys_to_delete.append(key)
    >>> for key in keys_to_delete:
    >>>     del my_dict[key]

    With the following:

    >>> with DictDeleter(my_list) as ld:
    >>>     for key, value in ld.items():
    >>>         if value.should_delete():
    >>>             ld.delete()

    Note that a single DictDeleter running from a single context must be iterated on by only a
    single Thread as it keeps the state of iterator in itself, to prevent allocating new objects
    and slowing things down too much.

    This allocates only a single object per a call to delete().
    """
    __slots__ = ('dict_to_process', 'current_iterator', 'keys_to_delete', 'iter_mode',
                 'current_key')

    def __init__(self, dict_to_process: collections.abc.MutableMapping):
        self.dict_to_process = dict_to_process
        self.iter_mode = ITER_KEYS

    def __enter__(self):
        self.keys_to_delete = set()
        return self

    def __iter__(self):
        self.current_iterator = iter(self.dict_to_process.items())
        return self

    def __next__(self):
        key, value = next(self.current_iterator)  # raises StopIteration
        self.current_key = key
        if self.iter_mode == ITER_ITEMS:
            return key, value
        elif self.iter_mode == ITER_VALUES:
            return value
        elif self.iter_mode == ITER_KEYS:
            return key

    def items(self) -> 'DictDeleter':
        self.iter_mode = ITER_ITEMS
        return self

    def keys(self) -> 'DictDeleter':
        self.iter_mode = ITER_KEYS
        return self

    def values(self) -> 'DictDeleter':
        self.iter_mode = ITER_VALUES
        return self

    def delete(self) -> None:
        self.keys_to_delete.add(self.current_key)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.keys_to_delete:
            del self.dict_to_process[key]
        return False


DIR_FORWARD = 0
DIR_BACKWARD = 1


class ListDeleter(tp.Generic[T]):
    """
    Having problems deleting entries from your list while iterating on them? No problem. Just swap
    the following:

    >>> entries_to_delete = []
    >>> for entry in my_list:
    >>>     if entry.should_delete():
    >>>         entries_to_delete.append(entry)
    >>> for entry in entries_to_delete:
    >>>     my_list.remove(entry)

    With the following:

    >>> with ListDeleter(my_list) as ld:
    >>>     for entry in ld:
    >>>         if entry.should_delete():
    >>>             ld.delete()

    Note that a single ListDeleter running from a single context must be iterated on by only a
    single Thread as it keeps the state of iterator in itself, to prevent allocating new objects
    and slowing things down too much.

    This allocates only a single object per a call to delete().

    Calling the list deleter during iteration will yield the element.

    You can pass any type of object here, as long as it supports pop(position) and __getitem__
    """
    __slots__ = ('list_to_process', 'current_index', 'indices_to_delete', 'direction')

    def __init__(self, list_to_process: tp.MutableSequence[T]):
        self.list_to_process = list_to_process
        self.direction = DIR_FORWARD
        # pointer to currently processed element
        self.current_index = -1 if self.direction == DIR_FORWARD else len(self.list_to_process)
        self.indices_to_delete = set()      # type: tp.Set[int]

    def __enter__(self) -> 'ListDeleter':
        return self

    @property
    def value(self) -> T:
        return self()

    def __call__(self) -> T:
        """
        Return current element
        """
        return self.list_to_process[self.current_index]

    def __iter__(self) -> 'ListDeleter':
        self.current_index = -1 if self.direction == DIR_FORWARD else len(self.list_to_process)
        self.indices_to_delete = set()
        return self

    def __next__(self):
        if self.direction == DIR_BACKWARD and self.current_index == 0:
            raise StopIteration('First element reached')
        if self.direction == DIR_FORWARD and self.current_index == len(self.list_to_process) - 1:
            raise StopIteration('Last element reached')
        self.current_index += +1 if self.direction == DIR_FORWARD else -1
        return self.list_to_process[self.current_index]

    def next(self) -> T:
        """
        :return: the next element
        :raises StopIteration: no more entries
        """
        next(self)
        return self.list_to_process[self.current_index]

    def prev(self) -> T:
        """
        Move to previous element

        :return: the previous element
        :raises ValueError: list is already at the first element!
        """
        if self.direction == DIR_FORWARD and self.current_index == 0:
            raise ValueError('Cannot go previous on a first element!')
        if self.direction == DIR_BACKWARD and self.current_index == len(self.list_to_process) - 1:
            raise ValueError('Cannot go previous on a last element!')
        self.current_index += -1 if self.direction == DIR_FORWARD else +1
        return self.list_to_process[self.current_index]

    def delete(self) -> None:
        self.indices_to_delete.add(self.current_index)

    def __reversed__(self) -> 'ListDeleter':
        """
        Take care, for this will modify the current object.

        This is done not to break the context manager semantics, and enable this:
        >>> with ListDeleter(a):
        >>>     for v in reversed(a):
        >>>         ...
        """
        if self.direction == DIR_BACKWARD:
            self.direction = DIR_FORWARD
            self.current_index = -1
        else:
            self.direction = DIR_BACKWARD
            self.current_index = len(self.list_to_process)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        index_delta = 0
        for index, element in enumerate(self.list_to_process[:]):
            if index in self.indices_to_delete:
                self.list_to_process.pop(index - index_delta)
                index_delta += 1

        return False

    def __copy__(self) -> 'ListDeleter':
        ld = ListDeleter(self.list_to_process)
        ld.direction = self.direction
        ld.current_index = self.current_index
        ld.indices_to_delete = copy.copy(self.indices_to_delete)
        return ld
