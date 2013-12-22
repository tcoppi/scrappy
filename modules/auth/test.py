from ..test_module import TestModule
from mock import Mock, patch

import auth

class TestAuth(TestModule):
    def setUp(self):
        super(TestAuth, self).setUp()
        self.auth_obj = auth.auth(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
