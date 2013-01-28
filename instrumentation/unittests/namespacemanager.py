from satella.instrumentation.insmgr import InstrumentationManager, NamespaceManager
from satella.instrumentation.exceptions import NamespaceExists, NamespaceNotExists

import unittest

class NamespaceManagerTest(unittest.TestCase):

    def test_adding_removing(self):
        nsm = NamespaceManager()
        insmgr = InstrumentationManager('test_namespace')

        nsm.add_namespace(insmgr)
        nsm.remove_namespace(insmgr)

    def test_multiadd_fail(self):
        nsm = NamespaceManager()
        insmgr = InstrumentationManager('test_namespace')

        nsm.add_namespace(insmgr)
        self.assertRaises(NamespaceExists, nsm.add_namespace, insmgr)

    def test_unfound_delete_fail(self):
        nsm = NamespaceManager()
        insmgr = InstrumentationManager('test_namespace')

        self.assertRaises(NamespaceNotExists, nsm.remove_namespace, insmgr)        