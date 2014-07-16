from ..test_module import TestModule
from mock import Mock, patch

import quote

class TestQuote(TestModule):
    def setUp(self):
        super(TestQuote, self).setUp()
        self.quote_obj = quote.quote(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
