import logging
import os, os.path
import sqlite3

class ModuleException(Exception):
    pass

# One object per scrappy!
class Module(object):
    def __init__(self, scrap):
        self.command_callbacks = {}
        self.logger = logging.getLogger("scrappy.%s" % self.__class__.__name__)

        if os.path.exists("db") and not os.path.isdir("db"):
            self.logger.critical("Databases directory 'db' is not a directory!")
            raise ModuleException("Databases directory 'db' is not a directory.")

        if not os.path.exists("db"):
            self.logger.debug("Creating database directory.")
            os.mkdir("db")

        conn = sqlite3.connect('db/%s.db' % self.__class__.__name__)
        conn.close()


    # Don't forget to close it!
    def get_db(self):
        conn = sqlite3.connect('db/%s.db' % self.__class__.__name__)
        return conn

    def register_cmd(self, cmd, callback):
        if cmd not in self.command_callbacks:
            self.command_callbacks[cmd] = []

        self.command_callbacks[cmd].append(callback)

    def get_help(self, server):
        docstrings = set()
        for command in self.command_callbacks:
            callback_list = self.command_callbacks[command]
            for callback in callback_list:
                doc = callback.__doc__
                doc = "%s%s\n%s" % (server["cmdchar"], command, doc)
                docstrings.add(doc)
        return docstrings

    def distribute(self, server, event, bot):
        if event.iscmd: # event is command
            command = event.cmd.split(" ")[0]
            if command in self.command_callbacks:
                for callback in self.command_callbacks[command]:
                    callback(server, event, bot)


