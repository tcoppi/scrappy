# Todo module
# Keeps track of todos and prioritizes them with a simple +/- system
from module import Module

import peewee

class Todo(peewee.Model):
    channel = peewee.TextField()
    server = peewee.TextField()
    todo = peewee.TextField()
    done = peewee.BooleanField(default=False)

    class Meta:
        database = peewee.SqliteDatabase('db/%s.db' % __name__.split('.')[0], threadlocals=True)

class todo(Module):
    models = [Todo]
    def __init__(self, scrap):
        super(todo, self).__init__(scrap)

        scrap.register_event("todo", "msg", self.distribute)

        self.register_cmd("todo", self.get_todo)
        self.register_cmd("todo-add", self.add_todo)
        self.register_cmd("todo-del", self.del_todo)
        self.register_cmd("todo-done", self.done_todo)

    # TODO: Paginate if the list gets too long?
    def get_todo(self, server, event, bot):
        conn = server["connection"]
        if len(event.arg) == 1:
            try:
                num = int(event.arg[0])
                todos = Todo.select().where(Todo.server==server["servername"], Todo.channel==event.target, Todo.id==num)
            except ValueError:
                if event.arg[0] == "all":
                    todos = Todo.select().where(Todo.server==server["servername"], Todo.channel==event.target).order_by(Todo.id.asc())
                else:
                    conn.privmsg(event.target, "%s is either not a valid todo ID or %stodo argument" % (event.arg[0], server["cmdchar"]))
                    return
        elif len(event.arg) > 1:
            #TODO: Tell the user what the correct syntax is
            conn.privmsg(event.target, "Incorrect syntax")
            return
        else:
            todos = Todo.select().where(Todo.server==server["servername"], Todo.channel==event.target, Todo.done==False).order_by(Todo.id.asc())

        if todos.count() == 0:
            conn.privmsg(event.target, "No todos for %s@%s" % (event.target, server["servername"]))

        for _todo in todos:
            todo_str = "Todo %d: %s" % (_todo.id, _todo.todo)
            if _todo.done:
                todo_str = "\x02%s Done\x02" % todo_str
            conn.privmsg(event.target, todo_str)

    def del_todo(self, server, event, bot):
        conn = server["connection"]
        if len(event.arg) == 1:
            try:
                num = int(event.arg[0])
            except ValueError:
                conn.privmsg(event.target, "%s not a valid todo ID" % num)
                return
        else:
            #TODO: Tell the user correct syntax
            conn.privmsg(event.target, "Incorrect syntax")
            return

        dq = Todo.delete().where(Todo.server==server["servername"], Todo.channel==event.target, Todo.id==num)
        deleted = dq.execute()

        if deleted:
            conn.privmsg(event.target, "Todo %d removed" % num)
        else:
            conn.privmsg(event.target, "Todo %d does not exist." % num)


    def done_todo(self, server, event, bot):
        conn = server["connection"]
        if len(event.arg) == 1:
            try:
                num = int(event.arg[0])
            except ValueError:
                conn.privmsg(event.target, "%s not a valid todo ID" % num)
                return
        else:
            #TODO: Tell the user correct syntax
            conn.privmsg(event.target, "Incorrect syntax")
            return

        q = Todo.update(done=True).where(Todo.server==server["servername"], Todo.channel==event.target, Todo.id==num)
        if q.execute() == 0:
            conn.privmsg(event.target, "Todo %d does not exist." % num)
        else:
            conn.privmsg(event.target, "Todo %d set done" % num)

    def add_todo(self, server, event, bot):
        conn = server["connection"]
        if len(event.arg) == 0:
            #TODO: Tell the user correct syntax
            conn.privmsg(event.target, "Incorrect syntax")
            return

        todo_text = " ".join(event.arg)

        new_todo = Todo(server=server["servername"], channel=event.target, done=False, todo=todo_text)
        new_todo.save()
        conn.privmsg(event.target, "Todo %d added" % new_todo.id)
