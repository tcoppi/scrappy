# Todo module
# Keeps track of todos and prioritizes them with a simple +/- systemwq
# Guarantees that no duplicate priorities are used by swapping todos if there is an adjacent priority
# TODO: set up a table for every channel
from module import Module

class todo(Module):
    def __init__(self, scrap):
        super(todo, self).__init__(scrap)

        scrap.register_event("todo", "msg", self.distribute)

        self.register_cmd("todo", self.todo)
        self.register_cmd("todo-list", self.list_todo)

    def todo(self, server, event, bot):
        conn = server["connection"]


        if len(event.arg) == 0:
            self.list_todo(server, event, bot)
            return

        try:
            num = int(event.arg[0])
            if len(event.arg) == 2:
                if event.arg[1] == "del":
                    deleted = self.remove(num, server, event.target)
                    if deleted:
                        conn.privmsg(event.target, "Removed todo %d." % num)
                    else:
                        conn.privmsg(event.target, "Todo %d does not exist." % num)

                elif event.arg[1] == "done":
                    done = self.set_done(num, server, event.target)
                    if done:
                        conn.privmsg(event.target, "Todo %d set done." % num)
                    else:
                        conn.privmsg(event.target, "Todo %d does not exist." % num)
                elif event.arg[1] == "++":
                    raised = self.raise_priority(num, server, event.target)
                    if raised:
                        conn.privmsg(event.target, "Todo %d priority raised." % num)
                    else:
                        conn.privmsg(event.target, "Todo %d does not exist." % num)
                elif event.arg[1] == "--":
                    lowered = self.lower_priority(num, server, event.target)
                    if lowered:
                        conn.privmsg(event.target, "Todo %d priority lowered." % num)
                    else:
                        conn.privmsg(event.target, "Todo %d does not exist." % num)
            elif len(event.arg) > 2:
                conn.privmsg(event.target, "Invalid operation on todo %d." % num)
            elif len(event.arg) < 2:
                todo = self.get_todo(num, server, event.target)
                if todo is not None:

                    msg = "Todo %d : %s" % (num, todo[0])
                    if todo[1] == 1:
                        msg += " (complete)"
                    else:
                        msg += " (incomplete)"
                    conn.privmsg(event.target, msg)
                else:
                    conn.privmsg(event.target, "Todo %d does not exist." % num)

        except ValueError:
            todo_item = " ".join(event.arg)
            num = self.add_todo(todo_item, server, event.target)
            conn.privmsg(event.target, "Todo %d added." % num)

    def setup_table(self, server, target):
        db_conn = self.get_db()
        # TODO: Could probably hash this, if there is no need to go from table->server/target again
        table_name = self.table_name(server, target)
        sql = "CREATE TABLE IF NOT EXISTS %s (priority INTEGER, todo TEXT, done INTEGER DEFAULT 0)" % table_name
        db_cursor = db_conn.cursor()
        db_cursor.execute(sql)
        db_conn.commit()
        db_conn.close()

    def table_name(self, server, target):
        table_name = server+target
        table_name = table_name.replace("[","").replace("]","")
        table_name = "["+table_name+"]"
        return table_name

    # TODO: Paginate if the list gets too long?
    def list_todo(self, server, event, bot):
        conn = server["connection"]
        self.setup_table(server["servername"], event.target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        table_name = self.table_name(server["servername"], event.target)

        sql = "SELECT rowid, todo FROM %s WHERE done=0 ORDER BY priority DESC" % table_name
        db_curs.execute(sql)

        todos = db_curs.fetchall()

        db_conn.close()

        for todo in todos:
            conn.privmsg(event.target, "Todo %d : %s" % (todo[0], todo[1]))

    def remove(self, num, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        table_name = self.table_name(server["servername"], target)

        sql = "DELETE FROM %s WHERE rowid=?" % table_name
        deleted = db_curs.execute(sql, (num,))

        db_conn.commit()
        db_conn.close()

        return deleted

    def set_done(self, num, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        table_name = self.table_name(server["servername"], target)

        sql = "SELECT 1 FROM %s WHERE rowid=?" % table_name
        db_curs.execute(sql, (num,))
        if db_curs.fetchone() is None:
            db_conn.close()
            return False

        sql = "UPDATE %s SET done=1 WHERE rowid=?" % table_name
        db_curs.execute(sql, (num,))

        db_conn.commit()
        db_conn.close()

        return True

    def raise_priority(self, num, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()
        table_name = self.table_name(server["servername"], target)

        sql = "SELECT priority FROM %s WHERE rowid=? AND done=0" % table_name
        db_curs.execute(sql, (num,))
        todo = db_curs.fetchone()
        if todo is None:
            db_conn.close()
            return False

        priority = todo[0]
        new_priority = priority + 1

        sql = "SELECT rowid FROM %s WHERE priority=? AND done=0" % table_name
        db_curs.execute(sql, (new_priority,))

        todo = db_curs.fetchone()

        if todo is None:
            sql = "UPDATE %s SET priority=? WHERE rowid=?" % table_name
            db_curs.execute(sql, (new_priority, num))
        else:
            swap_with = todo[0]
            sql = "UPDATE %s SET priority=? WHERE rowid=?" % table_name
            db_curs.execute(sql, (new_priority, num))
            db_curs.execute(sql, (priority, swap_with))

        db_conn.commit()
        db_conn.close()
        return True

    def lower_priority(self, num, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()
        table_name = self.table_name(server["servername"], target)

        sql = "SELECT priority FROM %s WHERE rowid=? AND done=0" % table_name
        db_curs.execute(sql, (num,))
        todo = db_curs.fetchone()
        if todo is None:
            db_conn.close()
            return False

        priority = todo[0]
        new_priority = priority - 1

        sql = "SELECT rowid FROM %s WHERE priority=? AND done=0" % table_name
        db_curs.execute(sql, (new_priority,))

        todo = db_curs.fetchone()

        if todo is None:
            sql = "UPDATE %s SET priority=? WHERE rowid=?" % table_name
            db_curs.execute(sql, (new_priority, num))
        else:
            swap_with = todo[0]
            sql = "UPDATE %s SET priority=? WHERE rowid=?" % table_name
            db_curs.execute(sql, (new_priority, num))
            db_curs.execute(sql, (priority, swap_with))

        db_conn.commit()
        db_conn.close()
        return True

    def get_todo(self, num, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        table_name = self.table_name(server["servername"], target)

        sql = "SELECT todo, done FROM %s WHERE rowid=?" % table_name
        db_curs.execute(sql, (num,))

        todo = db_curs.fetchone()
        db_conn.close()

        return todo

    def add_todo(self, todo, server, target):
        self.setup_table(server["servername"], target)
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        table_name = self.table_name(server["servername"], target)

        go_lower = True
        priority = 1000
        while go_lower:
            sql = "SELECT 1 FROM %s WHERE priority=?" % table_name
            db_curs.execute(sql, (priority,))
            todo_list = db_curs.fetchone()

            if todo_list is None:
                self.logger.debug("Found empty slot at priority %d" % priority)
                break

            priority -= 1

        sql = "INSERT INTO %s (priority, todo) VALUES (?, ?)" % table_name
        db_curs.execute(sql, (priority, todo))
        sql = "SELECT rowid FROM %s WHERE priority=?" % table_name
        db_curs.execute(sql, (priority,))
        num = db_curs.fetchone()[0]
        db_conn.commit()
        db_conn.close()
        return num
