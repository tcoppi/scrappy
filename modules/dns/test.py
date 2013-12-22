import unittest
from mock import Mock, patch

# SUT
import dns

class TestDNS(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()
        self.server = Mock()
        self.event = Mock()
        self.dns_obj = dns.dns(self.bot)

    def test_single_token(self):
        attrs = {'target': 'channel', 'tokens':['!dns']}
        self.event.configure_mock(**attrs)
        self.dns_obj.dns(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', 'Nothing to look up, zoob!')

    @patch.object(dns, 'socket')
    def test_good_ip(self, mock_socket):
        attrs = {'target': 'channel', 'tokens':['!dns', '10.0.0.10']}
        self.event.configure_mock(**attrs)
        mock_socket.gethostbyaddr.return_value = ('scrappy.example', [], [])
        self.dns_obj.dns(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', '10.0.0.10 -> scrappy.example')

    @patch.object(dns, 'socket')
    def test_bad_ip(self, mock_socket):
        attrs = {'gaierror': Exception}
        mock_socket.configure_mock(**attrs)
        mock_socket.gethostbyaddr.side_effect = mock_socket.gaierror
        attrs = {'target': 'channel', 'tokens':['!dns', '10.0.0.10']}
        self.event.configure_mock(**attrs)
        self.dns_obj.dns(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "No result for '10.0.0.10'")

    @patch.object(dns, 'socket')
    def test_good_domain(self, mock_socket):
        attrs = {'target': 'channel', 'tokens':['!dns', 'scrappy.example']}
        self.event.configure_mock(**attrs)
        mock_socket.gethostbyname.return_value = '10.0.0.10'
        self.dns_obj.dns(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "scrappy.example -> 10.0.0.10")

    @patch.object(dns, 'socket')
    def test_bad_domain(self, mock_socket):
        attrs = {'gaierror': Exception}
        mock_socket.configure_mock(**attrs)
        mock_socket.gethostbyname.side_effect = mock_socket.gaierror
        attrs = {'target': 'channel', 'tokens':['!dns', 'scrappy.example']}
        self.event.configure_mock(**attrs)
        self.dns_obj.dns(self.server, self.event, self.bot)

        self.server.privmsg.assert_called_with('channel', "No result for 'scrappy.example'")

if __name__ == '__main__':
    unittest.main()


