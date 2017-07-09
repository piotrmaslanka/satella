# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import monotonic
import unittest
from satella.instrumentation import instrument, DEBUG, RUNTIME, DISABLED, manager


class TestInstrumentsAndMetrics(unittest.TestCase):

    def test_m1(self):
        root = manager.getInstrument(u'zomg')

        txt = root.get_log(u'dupa', detail=DEBUG, buffer_size=30)

        root.set_detail(DISABLED)
        txt.log(u'Dupa')
        self.assertEquals(len(txt.view()), 0)

        root.set_detail(DEBUG)

        st = monotonic.monotonic()

        for x in six.moves.xrange(0, 100):
            txt.log(u'Dupa'+str(x))

        self.assertEqual(len(txt.view()), 30)

        for i, q in enumerate(txt.view()):
            ts, m, txt = q
            self.assertGreaterEqual(m, st)
            self.assertEquals(u'Dupa'+str(70 + i), txt)

    def test_kids(self):
        root = manager.getInstrument(u'root')
        wtf = manager.getInstrument(u'root.wtf')
        zomg = manager.getInstrument(u'root.zomg')
        pira = manager.getInstrument(u'root.zomg.pira')
        kek = manager.getInstrument(u'root.kek')

        kids = root.get_children()
        self.assertTrue(wtf in kids)
        self.assertTrue(zomg in kids)
        self.assertTrue(pira not in kids)
        self.assertTrue(kek in kids)

        kids.set_detail(DISABLED)

    def test_avg(self):
        root = manager.getInstrument(u'root')

        cnt = root.get_counter(u'dupa', detail=RUNTIME)

        cnt.log(1)
        cnt.log(2)
        cnt.log(3)

        self.assertEquals(cnt.view(), (6, 3, 2.0))

        cnt = root.get_counter(u'dupa2', detail=RUNTIME)

        self.assertEquals(cnt.view()[:2], (0, 0))

        import math
        self.assertTrue(math.isnan(cnt.view()[2]))