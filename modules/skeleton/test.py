from ..test_module import TestModule
from mock import Mock, patch

import skeleton

class TestSkeleton(TestModule):
    def setUp(self):
        super(TestSkeleton, self).setUp()
        self.skeleton_obj = skeleton.skeleton(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
