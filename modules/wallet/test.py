from ..test_module import TestModule
from mock import Mock, patch

import wallet

class TestWallet(TestModule):
    def setUp(self):
        super(TestWallet, self).setUp()
        self.wallet_obj = wallet.wallet(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
