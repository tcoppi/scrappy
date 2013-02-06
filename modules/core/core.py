#Module for scrappy that implements some core commands, like 'help'

import os
import sys

from irclib import client as ircclient

from module import Module

class core(Module):
    def __init__(self, scrap):
        super(core, self).__init__(scrap)

        scrap.register_event("core", "msg", self.distribute)
        scrap.register_event("core", "welcome", self.join_default)
        scrap.register_event("core", "disconnect", self.check_connections)

        self.register_cmd("help", self.help_cmd)
        self.register_cmd("join", self.join_cmd)
        self.register_cmd("reboot", self.reboot_cmd)

    def help_cmd(self, server, event, bot):
        """help - Lists all available commands and their docstrings"""
        c = server["connection"]

        if len(event.cmd.split(" ")[1:]) > 0:
            param = event.cmd.split(" ")[1]
            if param in bot.modules:
                module = bot.modules[param]
                help_set = module.get_help(server)
                c.privmsg(event.nick, "Module: %s" % module.__class__.__name__)
                for docstring in help_set:
                    for part in docstring.split("\n"):
                        c.privmsg(event.nick,part)
            else:
                c.privmsg(event.target, "Module '%s' not loaded, so no help." % param)
        else:
            c.privmsg(event.target, "Help list too long, specify a module (see %smodlist.)" % server["cmdchar"])

    def join_cmd(self, server, event, bot):
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
            # Just in case execv fails
            sys.exit(0)

    def join_default(self, server, event, bot):
        for channel in server["channels"]:
            if ircclient.is_channel(channel):
                server["connection"].join(channel)

    def check_connections(self, server, event, bot):
        connected = False
        for server in bot.servers.values():
            if server["connection"] is not None:
                if server["connection"].is_connected():
                    connected = True
        if not connected:
            # No more events should be going, so we're ok to shut down
            bot.shutdown()
