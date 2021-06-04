import typing as tp

from satella.coding.structures import frozendict
from satella.json import JSONAble


def join_metric_data_name(prefix: str, name: str):
    if prefix == '':
        return name
    else:
        return prefix + '.' + name


class MetricData(JSONAble):
    __slots__ = ('name', 'value', 'labels', 'timestamp', 'internal')

    def __init__(self, name: str, value: float, labels: dict = None,
                 timestamp: tp.Optional[float] = None,
                 internal: bool = False):
        self.name = name  # type: str
        self.internal = internal  # type: bool
        self.value = value  # type: tp.Any
        self.labels = frozendict(labels) if labels is not None else frozendict()
        self.timestamp = timestamp  # type: tp.Optional[float]

    def add_labels(self, labels: dict) -> None:
        labels_current = dict(self.labels)
        labels_current.update(labels)
        self.labels = frozendict(labels_current)

    def __eq__(self, other: 'MetricData') -> bool:
        return self.labels == other.labels and self.name == other.name

    def prefix_with(self, prefix: str) -> None:
        self.name = join_metric_data_name(prefix, self.name)

    def postfix_with(self, postfix: str) -> None:
        self.name = join_metric_data_name(self.name, postfix)

    def __hash__(self):
        return hash(self.labels) ^ hash(self.name)

    def to_json(self, prefix: str = '') -> tp.Union[list, dict, str, int, float, None]:
        k = {
            '_name': join_metric_data_name(prefix, self.name),
            '_': self.value,
            **self.labels,
        }
        if self.timestamp is not None:
            k['_timestamp'] = self.timestamp
        if self.internal:
            k['_internal'] = True
        return k

    def __repr__(self):
        return 'MetricData(%s, %s, %s, %s)' % (repr(self.name), repr(self.value),
                                               repr(self.labels), repr(self.timestamp))

    @classmethod
    def from_json(cls, x: dict) -> 'MetricData':
        name = x.pop('_name')
        value = x.pop('_')
        timestamp = x.pop('_timestamp', None)
        internal = x.pop('_internal', False)
        return MetricData(name, value, x, timestamp, internal)

    def add_timestamp(self, timestamp: tp.Optional[float]):
        self.timestamp = timestamp


class MetricDataCollection(JSONAble):
    """
    A bunch of metric datas
    """
    __slots__ = ('values',)

    def add_labels(self, labels: dict) -> None:
        output = set()
        for child in self.values:
            child.add_labels(labels)
            output.add(child)
        self.values = output

    def __repr__(self):
        return 'MetricDataCollection(%s)' % (repr(self.values, ))

    def __init__(self, *values: tp.Union[MetricData, 'MetricDataCollection']):
        if len(values) == 1:
            if isinstance(values[0], MetricData):
                self.values = set(values)
            elif isinstance(values[0], MetricDataCollection):
                self.values = values[0].values
            else:
                self.values = set(values[0])
        else:
            assert all(map(lambda x: isinstance(x, MetricData), values)), 'Not all arguments are ' \
                                                                          'MetricData!'
            self.values = set(values)

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        return [x.to_json() for x in self.values]

    def strict_eq(self, other: 'MetricDataCollection') -> bool:
        """
        Do values in other MetricDataCollection match also?
        """
        values_found = 0
        for value in self.values:
            for value_2 in other.values:
                if value == value_2:
                    values_found += 1
                    if value.value != value_2.value:
                        return False
                    break
            else:
                return False
        return values_found == len(other.values)

    @classmethod
    def from_json(cls, x: tp.List[dict]) -> 'MetricDataCollection':
        return MetricDataCollection(MetricData.from_json(y) for y in x)

    def __add__(self, other):
        if isinstance(other, MetricDataCollection):
            return self.__add_metric_data_collection(other)
        elif isinstance(other, MetricData):
            return self.__add_metric_data(other)
        raise TypeError('Unsupported addition with %s' % (other,))

    def prefix_with(self, prefix: str) -> 'MetricDataCollection':
        """Prefix every child with given prefix and return self"""
        for child in self.values:
            child.prefix_with(prefix)

    def postfix_with(self, postfix: str) -> 'MetricDataCollection':
        """Postfix every child with given postfix and return self"""
        for child in self.values:
            child.postfix_with(postfix)
        return self

    def __add_metric_data(self, other: MetricData):
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

    def __iadd_metric_data(self, other: 'MetricData') -> 'MetricDataCollection':
        if other in self.values:
            self.values.remove(other)
        self.values.add(other)
        return self

    def __iadd__(self, other: tp.Union['MetricDataCollection', MetricData]) -> \
            'MetricDataCollection':
        if isinstance(other, MetricDataCollection):
            return self.__iadd_metric_data_collection(other)
        else:
            return self.__iadd_metric_data(other)

    def set_timestamp(self, timestamp: float) -> 'MetricDataCollection':
        """Assign every child this timestamp and return self"""
        for child in self.values:
            child.add_timestamp(timestamp)
        return self

    def __eq__(self, other: 'MetricDataCollection') -> bool:
        return self.values == other.values

    def set_value(self, value) -> 'MetricDataCollection':
        """Set all children to a particular value and return self. Most useful"""
        for child in self.values:
            child.value = value
        return self

    def remove_internals(self):
        """
        Remove entries marked as internal
        """
        self.values = {value for value in self.values if not value.internal}
