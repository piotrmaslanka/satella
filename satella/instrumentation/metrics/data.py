import itertools
import typing as tp
import copy
import logging

from satella.coding.sequences import Multirun, n_th
from satella.json import JSONAble
from satella.coding.structures import frozendict, OmniHashableMixin
from satella.coding.structures import ReprableMixin

logger = logging.getLogger(__name__)


def join_metric_data_name(prefix: str, name: str):
    if prefix == '':
        return name
    elif name == '':
        return prefix
    else:
        return prefix+'.'+name


class MetricData(ReprableMixin, OmniHashableMixin, JSONAble):
    _REPR_FIELDS = ('name', 'value', 'labels')
    _HASH_FIELDS_TO_USE = ('name', 'labels')
    __slots__ = ('name', 'value', 'labels')

    def __init__(self, name: str, value: float, labels: tp.Optional[dict] = None):
        self.name = name                    # type: str
        self.value = value                  # type: tp.Any
        self.labels = frozendict(labels or ())                # type: frozendict

    def add_labels(self, labels: tp.Dict[str, tp.Any]) -> None:
        new_labels = dict(self.labels.items())
        new_labels.update(labels)
        self.labels = frozendict(new_labels)

    def prefix_with(self, prefix: str) -> None:
        self.name = join_metric_data_name(prefix, self.name)

    def postfix_with(self, postfix: str) -> None:
        self.name = join_metric_data_name(self.name, postfix)

    def to_json(self, prefix: str = '') -> list:
        return [join_metric_data_name(prefix, self.name), self.value, self.labels]

    @classmethod
    def from_json(cls, x: list) -> 'MetricData':
        return MetricData(*x)


class MetricDataContainer(ReprableMixin, OmniHashableMixin, JSONAble):
    _REPR_FIELDS = ('name', 'entries', 'description', 'type', 'internal', 'timestamp')
    __slots__ = ('name', 'entries', 'description', 'type', 'internal', 'timestamp')
    _HASH_FIELDS_TO_USE = ('name', 'entries')

    def __init__(self, principal_name: str, entries: tp.Optional[tp.Sequence[MetricData]] = None,
                 description: tp.Optional[str] = None,
                 metric_type: tp.Optional[str] = None,
                 internal: bool = False,
                 timestamp: tp.Optional[float] = None):
        self.name = principal_name
        self.entries = set(entries or ())
        self.description = description
        self.type = metric_type
        self.internal = internal
        self.timestamp = timestamp

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def rehash(self):   # to be invoked after each metricdata-altering operation
        items = self.entries
        self.entries = set()
        for item in items:
            self.entries.add(item)

    def prefix_with(self, val: str) -> 'MetricDataContainer':
        self.entries = set(Multirun(self).prefix_with(val))
        self.rehash()
        return self

    def postfix_with(self, val: str) -> 'MetricDataContainer':
        self.entries = set(Multirun(self).postfix_with(val))
        self.rehash()
        return self

    def add_labels(self, labels: tp.Dict[str, tp.Any]) -> 'MetricDataContainer':
        self.entries = set(Multirun(self).add_labels(labels))
        self.rehash()
        return self

    def extend(self, other: tp.Union['MetricDataContainer', tp.List[MetricData]]) -> None:
        if isinstance(other, MetricDataContainer):
            self.entries.update(other.entries)
        else:
            for elem in other:
                self.entries.add(elem)

    def __add__(self, other: MetricData) -> 'MetricDataContainer':
        assert not isinstance(other, MetricDataContainer), 'Use .extend()'
        my = copy.copy(self)
        if other in my.entries:
            my.entries.remove(other)
        my.entries.add(other)
        return my

    def __iadd__(self, other: MetricData) -> 'MetricDataContainer':
        assert not isinstance(other, MetricDataContainer), 'Use .extend()'
        if other in self.entries:
            self.entries.remove(other)
        self.entries.add(other)
        return self

    def to_json(self) -> dict:
        x = {
            'name': self.name,
            'entries': [x.to_json() for x in self.entries],
        }
        if self.internal:
            x['internal'] = True
        if self.description:
            x['description'] = self.description
        if self.timestamp:
            x['timestamp'] = self.timestamp
        if self.type:
            x['type'] = self.type
        return x

    @classmethod
    def from_json(cls, x: dict) -> 'MetricDataContainer':
        internal = x.pop('internal', False)
        description = x.pop('description', None)
        timestamp = x.pop('timestamp', None)
        metric_type = x.pop('type', None)
        name = x.pop('name')
        entries = [MetricData.from_json(y) for y in x.pop('entries')]
        return MetricDataContainer(name, entries, description, metric_type, internal, timestamp)

    def copy(self) -> 'MetricDataContainer':
        return copy.copy(self)


class MetricDataCollection(ReprableMixin, JSONAble):
    __slots__ = ('values', )
    _REPR_FIELDS = ('values', )

    def flatten(self) -> 'MetricDataCollection':
        """Make all MetricData in a single MetricDataContainer"""
        mdc = n_th(self.values).copy()
        mdc.entries = set()
        for child in self.values:
            for item in child.entries:
                mdc.entries.add(item)
        return MetricDataCollection([mdc])

    def __init__(self, values: tp.Optional[tp.Iterable[tp.Union[MetricDataContainer]]] = None):
        self.values = set(values or ())     # type: tp.Set[MetricDataContainer]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def rehash(self):
        """To be called after any hash-changing operation"""
        entries = self.values
        self.values = set()
        for item in entries:
            self.values.add(item)

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        return [x.to_json() for x in self]

    def add_labels(self, labels: tp.Dict[str, tp.Any]) -> None:
        self.__apply_to_children('add_labels', labels)
        self.rehash()

    def strict_eq(self, other: 'MetricDataCollection') -> bool:
        """
        Do values in other MetricDataCollection match also?
        """
        values_found = 0
        for value, value_2 in itertools.product(self, other):
            if value == value_2:
                values_found += 1
                if value.entries != value_2.entries:
                    return False
        return values_found == len(other.values)

    @classmethod
    def from_json(cls, x: tp.List[dict]) -> 'MetricDataCollection':
        return MetricDataCollection([MetricDataContainer.from_json(y) for y in x])

    def __add__(self, other):
        if isinstance(other, MetricDataCollection):
            return self.__add_metric_data_collection(other)
        elif isinstance(other, MetricDataContainer):
            self.__add_metric_data_container(other)
        raise TypeError('Unsupported addition with %s' % (other, ))

    def __apply_to_children(self, operation_name: str, *args, **kwargs) -> 'MetricDataCollection':
        # note that we need to update it this way as we are changing the hashes of the children
        getattr(Multirun(self, dont_return_list=True), operation_name)(*args, **kwargs)
        self.rehash()
        return self

    def prefix_with(self, prefix: str) -> 'MetricDataCollection':
        """Prefix every child with given prefix and return self"""
        s = self.__apply_to_children('prefix_with', prefix)
        return s

    def postfix_with(self, postfix: str) -> 'MetricDataCollection':
        """Postfix every child with given postfix and return self"""
        return self.__apply_to_children('postfix_with', postfix)

    def __add_metric_data_container(self, other: MetricDataContainer) -> 'MetricDataCollection':
        values = self.values.copy()
        if other in values:
            values.remove(other)
        values.add(other)
        return MetricDataCollection(values)

    def __add_metric_data_collection(self, other: 'MetricDataCollection') -> 'MetricDataCollection':
        b = other.values.copy()

        for c in self.values:
            if c not in b:
                b.add(c)

        return MetricDataCollection(b)

    def __iadd_metric_data_collection(self, other: 'MetricDataCollection') -> \
            'MetricDataCollection':
        other_values = other.values.copy()
        for elem in self.values:
            if elem not in other_values:
                other_values.add(elem)
        self.values = other_values
        return self

    def __iadd_metric_data_container(self, other: MetricDataContainer) -> 'MetricDataCollection':
        if other in self.values:
            self.values.remove(other)
        self.values.add(other)
        return self

    def __iadd__(self, other: tp.Union['MetricDataCollection', MetricDataContainer]) -> \
            'MetricDataCollection':
        if isinstance(other, MetricDataCollection):
            return self.__iadd_metric_data_collection(other)
        else:
            return self.__iadd_metric_data_container(other)

    def __eq__(self, other: 'MetricDataCollection') -> bool:
        return self.values == other.values
