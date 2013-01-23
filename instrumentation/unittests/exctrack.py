from satella.instrumentation.exctrack import Trackback

import unittest

class TrackbackTest(unittest.TestCase):

    def test_frames(self):

        # Hierarchy of functions
        def a():
            test = 5
            b()

        def b():
            fun = 'hello'
            c()

        def c():
            hello = None            
            raise ValueError, 'test exception'

        try:
            a()
        except:
            tb = Trackback()
        else:
            self.fail('test did not raise exception')

        self.assertEquals(tb.frames[0].locals['hello'].get_value(), None)
        self.assertEquals(tb.frames[1].locals['fun'].get_value(), 'hello')
        self.assertEquals(tb.frames[2].locals['test'].get_value(), 5)
        self.assertEquals(tb.frames[2].locals['test'].get_repr(), repr(5))        