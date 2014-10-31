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

    def test_interface(self):
                
        class AdditionInterface(TQM.Interface):
            def add2(self, val):
                self.queue.put(val+2)
                
            def add4(self, val):
                self.queue.put(val+4)
        
        tqm = TQM()
        tqm.register_interface('additor', AdditionInterface)
        
        reader = tqm.get_reader_for('additor')
        addition = tqm.get_interface_for('additor')
        
        addition.add2(8)
        addition.add4(8)
        
        self.assertEquals(reader.get(), 10)
        self.assertEquals(reader.get(), 12)
        
    def test_tqm_iterablereader(self):
        tqm = TQM()
        
        reader = tqm.get_reader_for('dupa')
        writer = tqm.get_writer_for('dupa')
        
        writer.put('A')
        writer.put('B')
        
        i = 0
        for msg in reader:
            self.assertEquals(msg, {0: 'A', 1: 'B'}[i])
            i += 1
            
        writer.put('C')
        writer.put('D')
        i = 0
        for msg in reader:
            self.assertEquals(msg, {0: 'C', 1: 'D'}[i])
            i += 1        
        
    def test_tqm_blockiterablereader(self):
        tqm = TQM()
        
        reader = tqm.get_reader_for('dupa', 1)
        writer = tqm.get_writer_for('dupa')
        
        writer.put('A')
        writer.put('B')
        
        i = 0
        for msg in reader:
            self.assertEquals(msg, {0: 'A', 1: 'B'}[i])
            i += 1
            
        writer.put('C')
        writer.put('D')
        i = 0
        for msg in reader:
            self.assertEquals(msg, {0: 'C', 1: 'D'}[i])
            i += 1                        
