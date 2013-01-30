#Module for scrappy that implements some core commands, like 'help'

import os
import sys

class core(object):
    def __init__(self, scrap):
        self.command_callbacks = {}
        scrap.register_event("core", "msg", self.distribute)
        #register commands
        #scrap.register_event("core", "msg", help_cmd)
        #scrap.register_event("core", "msg", join_cmd)
        self.register_cmd("help", self.help_cmd)
        self.register_cmd("join", self.join_cmd)
        self.register_cmd("reboot", self.reboot_cmd)

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

    def help_cmd(self, server,event,bot):
        """help - Lists all available commands and their docstrings"""
        c = server["connection"]

        #put the events into a set so we can compute the union
        #Or maybe we should use sets for the events from the start?

        for module in bot.modules.values():
            help_set = module.get_help(server)
            c.privmsg(event.nick, "Module: %s" % module.__class__.__name__)
            for docstring in help_set:
                for part in docstring.split("\n"):
                    c.privmsg(event.nick,part)


    def join_cmd(self, server,event,bot):
        """join a channel"""
        c = server["connection"]

        # Bot owner
        # TODO: Store in config
        if event.nick == "Landon":
            chan = event.cmd.split(" ")[1]
            c.join(chan)

    def reboot_cmd(self, server, event, bot):
        """ Reboot the bot """
        c = server["connection"]

        if event.nick == "Landon":
            for server in bot.servers.values():
                server["connection"].quit("BAIL OUT FOR REBOOT!!!")
            os.execv(bot.argv[0], bot.argv)


