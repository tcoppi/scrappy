from ..test_module import TestModule
from mock import Mock, patch

import gcalc

class TestGcalc(TestModule):
    def setUp(self):
        super(TestGcalc, self).setUp()
        self.gcalc_obj = gcalc.gcalc(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
