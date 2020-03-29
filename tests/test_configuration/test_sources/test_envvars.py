from satella.configuration import sources
from satella.configuration.sources import EnvVarsSource, OptionalSource, AlternativeSource, \
    EnvironmentSource, \
    StaticSource, MergingSource
from .utils import SourceTestCase, mock_env


class TestEnvVarsSource(SourceTestCase):
    @mock_env('satella', '{"a":2}')
    def test_ok(self):
        self.assertSourceHas(sources.EnvVarsSource('satella'), {u"a": 2})

    def test_none(self):
        self.assertSourceEmpty(OptionalSource(EnvVarsSource('satella')))
        self.assertSourceFails(EnvVarsSource('satella'))

    def test_alternative(self):
        ds = AlternativeSource(
            EnvironmentSource('test', 'test'),
            StaticSource({'test': 'test'})
        )
        self.assertSourceHas(ds, {'test': 'test'})

    def test_merging(self):
        ds = MergingSource(
            EnvironmentSource('test', 'test'),
            on_fail=MergingSource.SILENT,
            fail_if_no_sources_are_correct=False
        )
        self.assertEqual(ds.provide(), {})
