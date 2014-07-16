from ..test_module import TestModule
from mock import Mock, patch

import fact

class TestFact(TestModule):
    def setUp(self):
        super(TestFact, self).setUp()
        self.fact_obj = fact.fact(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
