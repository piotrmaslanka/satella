from satella.threads import create_pipes, Pipe
from time import sleep
import Queue

import unittest

class PipeTest(unittest.TestCase):

    def test_pipe(self):
        """Tests basic pipe predicaments"""

        a, b = create_pipes()
        
        a.put('Lol')
        
        self.assertEqual(b.get(), 'Lol')
        a.close()
        b.close()
        
    def test_pipe_others(self):
        """Tests queue_for_a"""

        someq = Queue.Queue()
        
        a, b = create_pipes(queue_for_a=someq)
        c, d = create_pipes(queue_for_a=someq)
        
        a.put('Lol')
        c.put('Hey')
        
        self.assertEqual(someq.get(), 'Lol')        
        self.assertEqual(someq.get(), 'Hey') 
        self.assertRaises(Pipe.Empty, b.get, False)
        self.assertRaises(Queue.Empty, b.get, False)        