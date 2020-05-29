import collections
from satella.coding.recast_exceptions import rethrow_as

ITER_KEYS = 0
ITER_VALUES = 1
ITER_ITEMS = 2


class DictDeleter:
    """
    Having problems deleting entries from your dict while iterating on them? No problem. Just swap the following:

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

    Note that a single DictDeleter running from a single context must be iterated on by only a single
    Thread as it keeps the state of iterator in itself, to prevent allocating new objects and slowing
    things down too much.

    This allocates only a single object per a call to delete().
    """
    __slots__ = ('dict_to_process', 'current_iterator', 'keys_to_delete', 'iter_mode', 'current_key')

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
        key, value = next(self.current_iterator)        # raises StopIteration
        self.current_key = key
        if self.iter_mode == ITER_ITEMS:
            return key, value
        elif self.iter_mode == ITER_VALUES:
            return value
        elif self.iter_mode == ITER_KEYS:
            return key

    def items(self):
        self.iter_mode = ITER_ITEMS
        return self

    def keys(self):
        self.iter_mode = ITER_KEYS
        return self

    def values(self):
        self.iter_mode = ITER_VALUES
        return self

    def delete(self):
        self.keys_to_delete.add(self.current_key)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.keys_to_delete:
            del self.dict_to_process[key]
        return False


class ListDeleter:
    """
    Having problems deleting entries from your list while iterating on them? No problem. Just swap the following:

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

    Note that a single ListDeleter running from a single context must be iterated on by only a single
    Thread as it keeps the state of iterator in itself, to prevent allocating new objects and slowing
    things down too much.

    This allocates only a single object per a call to delete().

    You can pass any type of object here, as long as it supports pop(position) and __getitem__
    """
    __slots__ = ('list_to_process', 'current_index', 'indices_to_delete')

    def __init__(self, list_to_process: collections.abc.MutableSequence):
        self.list_to_process = list_to_process

    def __enter__(self) -> 'ListDeleter':
        return self

    def __iter__(self) -> 'ListDeleter':
        self.current_index = 0
        self.indices_to_delete = set()
        return self

    @rethrow_as(IndexError, StopIteration)
    def __next__(self):
        self.current_index += 1
        return self.list_to_process[self.current_index-1]

    def delete(self) -> None:
        self.indices_to_delete.add(self.current_index-1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        index_delta = 0
        for index, element in enumerate(self.list_to_process[:]):
            if index in self.indices_to_delete:
                self.list_to_process.pop(index-index_delta)
                index_delta += 1

        return False
