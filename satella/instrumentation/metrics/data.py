import itertools
import typing as tp
import copy
import logging

from satella.coding.sequences import Multirun
from satella.json import JSONAble
from satella.coding.structures import frozendict
from satella.coding.structures import ReprableObject

logger = logging.getLogger(__name__)


def join_metric_data_name(prefix: str, name: str):
    if prefix == '':
        return name
    elif name == '':
        return prefix
    else:
        return prefix+'.'+name


class MetricData(ReprableObject, JSONAble):
    __slots__ = ('name', 'value', 'labels')

    def __init__(self, name: str, value: float, labels: tp.Optional[dict] = None):
        super().__init__(name, value)
        self.name = name                    # type: str
        self.value = value                  # type: tp.Any
        self.labels = frozendict(labels or ())                # type: frozendict

    def add_labels(self, labels: tp.Dict[str, tp.Any]) -> None:
        new_labels = dict(self.labels.items())
        new_labels.update(labels)
        self.labels = frozendict(new_labels)

    def __eq__(self, other: 'MetricData') -> bool:
        return self.name == other.name and self.labels == other.labels

    def prefix_with(self, prefix: str) -> None:
        self.name = join_metric_data_name(prefix, self.name)

    def postfix_with(self, postfix: str) -> None:
        self.name = join_metric_data_name(self.name, postfix)

    def __hash__(self):
        return hash(self.name) ^ hash(self.labels)

    def to_json(self, prefix: str = '') -> list:
        return [join_metric_data_name(prefix, self.name), self.value, self.labels]

    @classmethod
    def from_json(cls, x: list) -> 'MetricData':
        return MetricData(*x)

    def __repr__(self):
        return '%s %s' % (id(self), self.name)


class MetricDataContainer(ReprableObject, JSONAble):
    __slots__ = ('name', 'entries', 'description', 'type', 'internal', 'timestamp')

    def __init__(self, principal_name: str, entries: tp.Optional[tp.Sequence[MetricData]] = None,
                 description: tp.Optional[str] = None,
                 metric_type: tp.Optional[str] = None,
                 internal: bool = False,
                 timestamp: tp.Optional[float] = None):
        super().__init__(principal_name, entries, description, metric_type, internal, timestamp)
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

    def prefix_with(self, val: str):
        self.entries = set(Multirun(self).prefix_with(val))
        logger.warning(f'self.entries={self.entries}')

    def postfix_with(self, val: str):
        self.entries = set(Multirun(self).postfix_with(val))

    def add_labels(self, labels: tp.Dict[str, tp.Any]):
        self.entries = set(Multirun(self).add_labels(labels))

    def extend(self, other: 'MetricDataContainer') -> None:
        self.entries.update(other.entries)

    def __add__(self, other: MetricData) -> 'MetricDataContainer':
        my = copy.copy(self)
        if other in my.entries:
            my.entries.remove(other)
        my.entries.add(other)
        return my

    def __iadd__(self, other: MetricData) -> 'MetricDataContainer':
        if other in self.entries:
            self.entries.remove(other)
        self.entries.add(other)
        return self

    def __eq__(self, other: 'MetricDataContainer'):
        return self.entries == other.entries and self.name == other.name

    def __hash__(self) -> int:
        hash_value = 0
        for entry in self.entries:
            hash_value ^= hash(entry)
        return hash_value

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


class MetricDataCollection(ReprableObject, JSONAble):
    __slots__ = ('values', )

    def __init__(self, values: tp.Optional[tp.Iterable[tp.Union[MetricDataContainer]]] = None):
        super().__init__(values)
        self.values = set(values or ())     # type: tp.Set[MetricDataContainer]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        return [x.to_json() for x in self]

    def add_labels(self, labels: tp.Dict[str, tp.Any]) -> None:
        self.__apply_to_children('add_labels', labels)

    def strict_eq(self, other: 'MetricDataCollection') -> bool:
        """
        Do values in other MetricDataCollection match also?
        """
        values_found = 0
        logger.warning(f'Comparing {list(self.values)} against {list(other.values)}')
        for value, value_2 in itertools.product(self, other):
            if value == value_2:
                values_found += 1
                if value.entries != value_2.entries:
                    return False
                break
            else:
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
        self.values = set(getattr(Multirun(self), operation_name)(*args, **kwargs))
        return self

    def prefix_with(self, prefix: str) -> 'MetricDataCollection':
        """Prefix every child with given prefix and return self"""
        s = self.__apply_to_children('prefix_with', prefix)
        logger.warning(f'Append resulted in {list(self)}')
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
