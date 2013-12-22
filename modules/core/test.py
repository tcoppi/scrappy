from ..test_module import TestModule
from mock import Mock, patch

import core

class TestCore(TestModule):
    def setUp(self):
        super(TestCore, self).setUp()
        self.core_obj = core.core(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
