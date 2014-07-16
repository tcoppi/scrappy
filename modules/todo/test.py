from ..test_module import TestModule
from mock import Mock, patch

import todo

class TestTodo(TestModule):
    def setUp(self):
        super(TestTodo, self).setUp()
        self.todo_obj = todo.todo(self.bot)

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
