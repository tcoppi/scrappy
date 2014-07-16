from ..test_module import TestModule
from mock import Mock, patch

import insult

class TestInsult(TestModule):
    def setUp(self):
        super(TestInsult, self).setUp()
        self.insult_obj = insult.insult(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
