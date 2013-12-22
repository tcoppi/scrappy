from ..test_module import TestModule
from mock import Mock, patch

import url

class TestURL(TestModule):
    def setUp(self):
        super(TestURL, self).setUp()
        self.url_obj = url.url(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
