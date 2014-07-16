from ..test_module import TestModule
from mock import Mock, patch

import eve

class TestEve(TestModule):
    def setUp(self):
        super(TestEve, self).setUp()
        self.eve_obj = eve.eve(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
