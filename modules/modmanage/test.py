from ..test_module import TestModule
from mock import Mock, patch

import modmanage

class TestModmanage(TestModule):
    def setUp(self):
        super(TestModmanage, self).setUp()
        self.modmanage_obj = modmanage.modmanage(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
