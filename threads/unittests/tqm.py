from satella.threads import TQM
from time import sleep
import Queue

import unittest

class TQMTest(unittest.TestCase):

    def test_pipe(self):
        """Tests basic TQM predicaments"""

        tqm = TQM()
        
        reader = tqm.get_reader_for('dupa')
        writer = tqm.get_writer_for('dupa')
        
        writer.put_nowait('wtf')
        self.assertEqual(reader.get(), 'wtf')
        
    def test_multiwriter(self):
        """Tests queue_for_a"""
        
        tqm = TQM()
        reader1 = tqm.get_reader_for('dupa1')
        reader2 = tqm.get_reader_for('dupa2')
        
        writer = tqm.get_multiwriter(['dupa1', 'dupa2'])
        
        writer.put_nowait('wtf')
        self.assertEqual(reader1.get(), 'wtf')
        self.assertEqual(reader2.get(), 'wtf')
