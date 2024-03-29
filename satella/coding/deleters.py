import collections
import copy
import typing as tp

from satella.coding.typing import T

ITER_KEYS = 0
ITER_VALUES = 1
ITER_ITEMS = 2


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

    You can also use the alternative syntax of:
    >>> ld = ListDeleter(my_list)
    >>> while True:
    >>>     try:
    >>>         v = ld.next()
    >>>     except StopIteration:
    >>>         break
    >>>     if condition(v):
    >>>         ld.delete()
    >>> ld.remove_items()

    Note that a single ListDeleter running from a single context must be iterated on by only a
    single Thread as it keeps the state of iterator in itself, to prevent allocating new objects
    and slowing things down too much.

    Note that calling reversed() on this will reset the pointer to the end of the list
    or the beginning of the list, respectively.

    This allocates only a single object per a call to delete().

    Calling the list deleter during iteration will yield the element.

    You can pass any type of object here, as long as it supports pop(position) and __getitem__
    """
    __slots__ = 'list_to_process', 'current_index', 'indices_to_delete', 'direction', 'removed'

    def __init__(self, list_to_process: tp.MutableSequence[T], direction: int = DIR_FORWARD):
        self.list_to_process = list_to_process
        # pointer to currently processed element
        self.direction = direction
        self.current_index = -1 if direction == DIR_FORWARD else len(self.list_to_process)
        self.indices_to_delete = set()  # type: tp.Set[int]
        self.removed = False

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

    def __next__(self) -> T:
        if self.direction == DIR_BACKWARD and self.current_index == -1:
            raise StopIteration('First element reached')
        if self.direction == DIR_FORWARD and self.current_index == len(self.list_to_process):
            raise StopIteration('Last element reached')
        self.current_index += +1 if self.direction == DIR_FORWARD else -1
        try:
            return self.list_to_process[self.current_index]
        except IndexError:
            raise StopIteration()

    def next(self) -> T:
        """
        :return: the next element
        :raises StopIteration: no more entries
        """
        return next(self)

    def prev(self) -> T:
        """
        Move to previous element, as per ordering.

        :return: the previous element
        :raises StopIteration: list is already at the first element!
        """
        if self.direction == DIR_FORWARD and self.current_index == -1:
            raise StopIteration('Cannot go previous on a first element!')
        if self.direction == DIR_BACKWARD and self.current_index == len(self.list_to_process):
            raise StopIteration('Cannot go previous on a last element!')
        self.current_index += -1 if self.direction == DIR_FORWARD else +1
        try:
            return self.list_to_process[self.current_index]
        except IndexError:
            raise StopIteration()

    def delete(self) -> None:
        self.indices_to_delete.add(self.current_index)

    def __reversed__(self) -> 'ListDeleter':
        """
        This will return a new ListDeleter. Take care that it will break context managers
        such as this:

        >>> with ListDeleter(a):
        >>>     for v in reversed(a):
        >>>         ...

        It is much preferred to do the following in that case:

        >>> with reversed(ListDeleter(a)) as ld:
        >>>     for v in a:
        >>>         if condition(v):
        >>>             ld.delete()
        """
        if self.direction == DIR_BACKWARD:
            return ListDeleter(self.list_to_process)
        else:
            return ListDeleter(self.list_to_process, DIR_BACKWARD)

    def remove_items(self) -> None:
        """
        After all of the items have been marked for deletion, delete them
        """
        if not self.removed:
            index_delta = 0
            for index, element in enumerate(self.list_to_process[:]):
                if index in self.indices_to_delete:
                    self.list_to_process.pop(index - index_delta)
                    index_delta += 1
            self.removed = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_items()
        return False

    def __copy__(self) -> 'ListDeleter':
        ld = ListDeleter(self.list_to_process)
        ld.direction = self.direction
        ld.current_index = self.current_index
        ld.indices_to_delete = copy.copy(self.indices_to_delete)
        return ld
