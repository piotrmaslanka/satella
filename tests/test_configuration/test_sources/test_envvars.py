from satella.configuration.sources import EnvVarsSource, OptionalSource, AlternativeSource, EnvironmentSource, \
    StaticSource
from .utils import SourceTestCase, mock_env


class TestEnvVarsSource(SourceTestCase):
    @mock_env('satella', '{"a":2}')
    def test_ok(self):
        self.assertSourceHas(EnvVarsSource('satella'), {u"a": 2})

    def test_none(self):
        self.assertSourceEmpty(OptionalSource(EnvVarsSource('satella')))
        self.assertSourceFails(EnvVarsSource('satella'))

    def test_alternative(self):
        ds = AlternativeSource(
            EnvironmentSource('test', 'test'),
            StaticSource({'test': 'test'})
        )
        self.assertSourceHas(ds, {'test': 'test'})