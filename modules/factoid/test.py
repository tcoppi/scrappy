from ..test_module import TestModule
from mock import Mock, patch

import factoid

class TestFactoid(TestModule):
    def setUp(self):
        super(TestFactoid, self).setUp()
        self.factoid_obj = factoid.factoid(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
