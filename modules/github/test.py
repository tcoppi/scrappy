from ..test_module import TestModule
from mock import Mock, patch

import github

class TestGithub(TestModule):
    def setUp(self):
        super(TestGithub, self).setUp()
        self.github_obj = github.github(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
