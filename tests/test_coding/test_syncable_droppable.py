import bisect
import typing as tp
import unittest

from satella.coding.predicates import x
from satella.coding.sequences import index_of
from satella.coding.structures import DBStorage, SyncableDroppable
from satella.coding.typing import K, KVTuple, V


class Iterator:
    def __init__(self, db_storage, it: tp.Iterator):
        self.it = it
        self.db_storage = db_storage

    def __iter__(self):
        return self.it

    def __next__(self):
        return next(self.it)

    def close(self):
        self.db_storage.iterators -= 1


class MyDBStorage(DBStorage):
    def delete(self, key: K) -> None:
        index = index_of(x[0] == key, self.data)
        del self.data[index]

    def on_change_synced_up_to(self, synced_up_to: tp.Optional[K]) -> None:
        self.synced = synced_up_to

    def on_change_stop_entry(self, stop_entry: tp.Optional[K]) -> None:
        self.stopped = stop_entry

    def iterate(self, starting_key: tp.Optional[K]) -> tp.Iterator[KVTuple]:
        if starting_key is None:
            it = iter(self.data)
        else:
            index = bisect.bisect_left([y[0] for y in self.data], starting_key)
            it = iter(self.data[index:])
        self.iterators += 1
        return Iterator(self, it)

    def __init__(self):
        self.data = []          # type: tp.List[KVtuple]
        self.started = None
        self.stopped = None
        self.synced = None
        self.iterators = 0

    def on_change_start_entry(self, start_entry: tp.Optional[K]) -> None:
        self.started = start_entry

    def put(self, key: K, value: V) -> None:
        self.data.append((key, value))


class TestSyncableDroppable(unittest.TestCase):
    def test_sync_drop(self):
        db = MyDBStorage()
        sd = SyncableDroppable(db, None, None, None, 100, 200)
        sd.on_new_data(100, 5)
        sd.on_new_data(150, 5)
        sd.on_new_data(180, 5)
        sd.on_new_data(200, 5)
        sd.on_new_data(220, 5)
        self.assertEqual(sd.first_key_in_memory, 100)
        sd.cleanup_keep_in_memory()
        self.assertEqual(sd.stop_entry, 220)
        self.assertEqual(sd.start_entry, 100)
        self.assertEqual(sd.first_key_in_memory, 150)
        self.assertEqual(db.data, [(100, 5)])
        sd.on_new_data(305, 5)
        sd.on_new_data(400, 5)
        sd.cleanup_keep_in_db()
        self.assertEqual(sd.start_entry, 200)
        self.assertEqual(db.data, [])

        sd.cleanup_keep_in_memory()
        self.assertEqual(db.data, [(200, 5), (220, 5)])
        synces = list(sd.on_sync_request())
        self.assertEqual(synces, [(200, 5), (220, 5), (305, 5), (400, 5)])
        synced_up_to = synces[-1][0]
        sd.on_synced_up_to(synced_up_to)
        self.assertRaises(ValueError, sd.on_sync_request)
        sd.on_new_data(405, 5)
        sd.on_new_data(409, 5)
        synces = list(sd.on_sync_request())
        self.assertEqual(synces, [(405, 5), (409, 5)])
        sd.on_new_data(510, 5)
        sd.cleanup_keep_in_memory()
        self.assertEqual(db.data, [(200, 5), (220, 5), (305, 5), (400, 5), (405, 5), (409, 5)])
        self.assertEqual(list(sd.get_archive(220, 420)), [(220, 5), (305, 5), (400, 5), (405, 5), (409, 5)])
        sd.cleanup_keep_in_db()
        self.assertEqual(db.data, [(400, 5), (405, 5), (409, 5)])
        self.assertFalse(db.iterators)
        self.assertEqual(sd.get_latest_value(), (510, 5))
