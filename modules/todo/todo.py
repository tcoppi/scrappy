# Todo module
# Keeps track of todos and prioritizes them with a simple +/- system
from module import Module, DBModel

import peewee

class Todo(DBModel):
    channel = peewee.TextField()
    server = peewee.TextField()
    todo = peewee.TextField()
    done = peewee.BooleanField(default=False)

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
        if len(event.arg) == 1:
            try:
                num = int(event.arg[0])
                todos = Todo.select().where(Todo.server==server.server_name, Todo.channel==event.target, Todo.id==num)
            except ValueError:
                if event.arg[0] == "all":
                    todos = Todo.select().where(Todo.server==server.server_name, Todo.channel==event.target).order_by(Todo.id.asc())
                else:
                    server.privmsg(event.target, "%s is either not a valid todo ID or %stodo argument" % (event.arg[0], server.cmdchar))
                    return
        elif len(event.arg) > 1:
            #TODO: Tell the user what the correct syntax is
            server.privmsg(event.target, "Incorrect syntax")
            return
        else:
            todos = Todo.select().where(Todo.server==server.server_name, Todo.channel==event.target, Todo.done==False).order_by(Todo.id.asc())

        if todos.count() == 0:
            server.privmsg(event.target, "No todos for %s@%s" % (event.target, server.server_name))

        for _todo in todos:
            todo_str = "Todo %d: %s" % (_todo.id, _todo.todo)
            if _todo.done:
                todo_str = "\x02%s Done\x02" % todo_str
            server.privmsg(event.target, todo_str)

    def del_todo(self, server, event, bot):
    	    
    	    #split on '-' to accept both todo-del X and todo-del X-Y
    	    items = event.arg[0].split('-')

    	    if len(items) > 2:
    	    	    server.privmsg(event.target, "Incorrect syntax")
    	    	    return
    	    elif len(items) == 1:
    	    	    #remove a single item
    	    	    try:
    	    	    	    item = int(items[0])
    	    	    except ValueError:
    	    	    	    server.privmsg(event.target, "%s not a valid todo ID" % item)
    	    	    	    return
    	    	    dq = Todo.delete().where(Todo.server == server.server_name, Todo.channel == event.target, Todo.id == item)
    	    	    deleted = dq.execute()
    	    	    
    	    	    if deleted:
    	    	    	    server.privmsg(event.target, "Todo %d removed" % item)
    	    	    else:
    	    	    	    server.privmsg(event.target, "Todo %d does not exist." % item)
    	    	    	    
    	    elif len(items) == 2:
    	    	    #remove range of items
    	    	    start = int(items[0])
    	    	    end = int(items[1])
    	    	    
    	    	    if end <= start:
    	    	    	    server.privmsg(event.target, "Invalid range.")
    	    	    	    return
    	    	    
    	    	    while start <= end:
    	    	    	    dq = Todo.delete().where(Todo.server == server.server_name, Todo.channel == event.target, Todo.id == start)
    	    	    	    deleted = dq.execute()
    	    	    	    
    	    	    	    if deleted:
    	    	    	    	    server.privmsg(event.target, "Todo %d removed" % start)
    	    	    	    else:
    	    	    	    	    server.privmsg(event.target, "Todo %d does not exist." % start)
    	    	    	    	    
    	    	    	    start += 1
    	    

    	    


    def done_todo(self, server, event, bot):
        if len(event.arg) == 1:
            try:
                num = int(event.arg[0])
            except ValueError:
                server.privmsg(event.target, "%s not a valid todo ID" % num)
                return
        else:
            #TODO: Tell the user correct syntax
            server.privmsg(event.target, "Incorrect syntax")
            return

        q = Todo.update(done=True).where(Todo.server==server.server_name, Todo.channel==event.target, Todo.id==num)
        if q.execute() == 0:
            server.privmsg(event.target, "Todo %d does not exist." % num)
        else:
            server.privmsg(event.target, "Todo %d set done" % num)

    def add_todo(self, server, event, bot):
        if len(event.arg) == 0:
            #TODO: Tell the user correct syntax
            server.privmsg(event.target, "Incorrect syntax")
            return

        todo_text = " ".join(event.arg)

        new_todo = Todo(server=server.server_name, channel=event.target, done=False, todo=todo_text)
        new_todo.save()
        server.privmsg(event.target, "Todo %d added" % new_todo.id)
