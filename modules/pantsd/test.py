from ..test_module import TestModule
from mock import Mock, patch

import pantsd

class TestPantsd(TestModule):
    def setUp(self):
        super(TestPantsd, self).setUp()
        self.pantsd_obj = pantsd.pantsd(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
