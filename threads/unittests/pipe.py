from satella.threads import create_pipes
from time import sleep

import unittest

class PipeTest(unittest.TestCase):

    def test_pipe(self):
        """Tests basic pipe predicaments"""

        a, b = create_pipes()
        
        a.put('Lol')
        
        self.assertEqual(b.get(), 'Lol')