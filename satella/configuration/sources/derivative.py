from satella.coding.algos import merge_dicts
from satella.exceptions import ConfigurationError
from .base import BaseSource

__all__ = [
    'AlternativeSource', 'OptionalSource', 'MergingSource'
]


class AlternativeSource(BaseSource):
    """
    If first source of configuration fails with ConfigurationError, use the next one instead, ad
    nauseam.
    """
    __slots__ = ('sources',)

    def __init__(self, *sources: BaseSource):
        super().__init__()
        self.sources = sources  # type: tp.List[BaseSource]

    def __repr__(self) -> str:
        return 'AlternativeSource(%s)' % (repr(self.sources),)

    def provide(self) -> dict:
        """
        :raises ConfigurationError: when backup fails too
        """
        for source in self.sources:
            try:
                s = source.provide()
                assert isinstance(s, dict), 'provide() returned a non-dict'
                return s
            except ConfigurationError:
                pass
        else:
            raise ConfigurationError('all sources failed!')


class OptionalSource(AlternativeSource):
    """
     This will substitute for empty dict if underlying config would fail.

     Apply this to your sources if you expect that they will fail.

     Use as

     >>> OptionalSource(SomeOtherSource1)
     """

    def __init__(self, source: BaseSource):
        super().__init__(source, BaseSource())

    def __repr__(self) -> str:
        return 'OptionalSource(%s)' % (repr(self.sources[0], ))


class MergingSource(BaseSource):
    """
    Source that merges configuration from a bunch of sources. The configuration has to be a
    dictionary!!

    :param sources: Sources to examine. Source later in queue will override earlier's entries, so
        take care.
    :param on_fail: how to behave when a source fails
    :param fail_if_no_sources_are_correct: even if on_fail == MergingSource.SILENT,
        if all sources fail, this will fail as well. Of course this makes sense only if on_fail ==
        MergingSource.SILENT
    """

    RAISE = 0  # Raise ConfigurationError if one of sources fails
    SILENT = 1  # Silently continue loading from next files if one fails
    __slots__ = ('sources', 'on_fail', 'fail_if_no_sources_are_correct')

    def __init__(self, *sources: BaseSource, on_fail: int = RAISE,
                 fail_if_no_sources_are_correct: bool = True):
        super().__init__()
        self.sources = sources
        self.on_fail = on_fail
        self.fail_if_no_sources_are_correct = fail_if_no_sources_are_correct

    def provide(self) -> dict:
        cfg = {}
        correct_sources = 0

        for source in self.sources:
            try:
                p = source.provide()
                correct_sources += 1
            except ConfigurationError as e:
                if self.on_fail == MergingSource.RAISE:
                    raise e
                elif self.on_fail == MergingSource.SILENT:
                    p = {}
                else:
                    raise ConfigurationError('Invalid on_fail parameter %s' % (self.on_fail,))
            assert isinstance(p, dict), 'what was provided by the config was not a dict'
            cfg = merge_dicts(cfg, p)
            assert isinstance(cfg, dict), 'what merge_dicts returned wasn''t a dict'

        if correct_sources == 0 and self.sources and self.fail_if_no_sources_are_correct:
            raise ConfigurationError('No source was able to load the configuration')

        return cfg

    def __repr__(self) -> str:
        return '<MergingSource %s>' % (repr(self.sources),)
