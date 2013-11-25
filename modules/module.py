import logging
import os, os.path
import time

import peewee

class DBModel(peewee.Model):
    #TODO: hardcoded, tut
    class Meta:
        database = peewee.SqliteDatabase('scrappy.db', threadlocals=True)

class ModuleException(Exception):
    pass

# One object per scrappy!
class Module(object):
    models = []

    def __init__(self, scrap):
        self.command_callbacks = {}
        self.logger = logging.getLogger("scrappy.%s" % self.__class__.__name__)

        for model in self.models:
            if not model.table_exists():
                model.create_table()

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
        event.tokens = event.arguments[0].split(" ")
        if not event.tokens:
            return

        if not event.tokens[0]:
            return

        event.arg = event.tokens[1:]
        event.command = event.tokens[0][1:]
        cmdchar = event.tokens[0][0]

        if cmdchar == server["cmdchar"]: # event is command
            if event.command in self.command_callbacks:
                for callback in self.command_callbacks[event.command]:
                    start = time.time()
                    callback(server, event, bot)
                    end = time.time()
                    self.logger.debug("Command timing: %fs for %s " % (end-start, event.command))
