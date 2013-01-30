#Module for scrappy that implements some core commands, like 'help'

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

    def register_cmd(self, cmd, callback):
        if cmd not in self.command_callbacks:
            self.command_callbacks[cmd] = []

        self.command_callbacks[cmd].append(callback)

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

        s1 = set()
        s2 = set()

        for event in bot.events["privmsg"].values():
            s1.add(event.__doc__)
        for event in bot.events["pubmsg"].values():
            s2.add(event.__doc__)

        funcnames = s1.union(s2)

        for name in funcnames:
            c.privmsg(event.nick,name)

    def join_cmd(self, server,event,bot):
        """join a channel"""
        c = server["connection"]

        # Bot owner
        if event.nick == "Landon":
            chan = event.cmd.split(" ")[1]
            c.join(chan)

