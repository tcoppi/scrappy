from ..test_module import TestModule
from mock import Mock, patch

import git

class TestGit(TestModule):
    def setUp(self):
        super(TestGit, self).setUp()
        self.git_obj = git.git(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
