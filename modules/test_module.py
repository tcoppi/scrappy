import unittest
from mock import Mock

class TestModule(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()
        self.server = Mock()
        self.event = Mock()
