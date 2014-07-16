from ..test_module import TestModule
from mock import Mock, patch

import reverse

class TestReverse(TestModule):
    def setUp(self):
        super(TestReverse, self).setUp()
        self.reverse_obj = reverse.reverse(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
