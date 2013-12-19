import unittest
from mock import Mock, patch

# SUT
import floatmod

class TestModule(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()
        self.server = Mock()
        self.event = Mock()

class TestFloatMod(TestModule):
    def setUp(self):
        super(TestFloatMod, self).setUp()
        self.floatmod_obj = floatmod.floatmod(self.bot)

class TestFloatCmd(TestFloatMod):
    def test_single_token(self):
        attrs = {'target': 'channel', 'tokens':['!$']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.float_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "Not enough arguments, <NUMBER> required.")

    def test_float(self):
        attrs = {'target': 'channel', 'tokens':['!$', '5.0']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.float_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "5.0: 32bit float:0x40a00000 | 2's complement int: 0x00000005 | 64bit float:0x4014000000000000 | 2's complement long: 0x0000000000000005")

    def test_hex(self):
        attrs = {'target': 'channel', 'tokens':['!$', '0x7']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.float_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "0x7: 32bit float:0x40e00000 | 2's complement int: 0x00000007 | 64bit float:0x401c000000000000 | 2's complement long: 0x0000000000000007")

    def test_bad_num(self):
        attrs = {'target': 'channel', 'tokens':['!$', 'EBADNUM']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.float_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "EBADNUM: Invalid number")

class TestBSCmd(TestFloatMod):
    def test_single_token(self):
        attrs = {'target': 'channel', 'tokens':['!$']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.float_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "Not enough arguments, <NUMBER> required.")

    def test_int(self):
        attrs = {'target': 'channel', 'tokens':['!bs', '5']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.bs_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', '5: 0x05000000')

    def test_hex(self):
        attrs = {'target': 'channel', 'tokens':['!bs', '0x7']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.bs_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', '0x7: 0x07000000')

    def test_bad_num(self):
        attrs = {'target': 'channel', 'tokens':['!bs', 'EBADNUM']}
        self.event.configure_mock(**attrs)

        self.floatmod_obj.bs_cmd(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', 'EBADNUM: Invalid number')

if __name__ == '__main__':
    unittest.main()


