from ..test_module import TestModule
from mock import Mock, patch

import markov

class TestMarkov(TestModule):
    def setUp(self):
        super(TestMarkov, self).setUp()
        self.markov_obj = markov.markov(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
