#stuff for loading/unloading/managing/getting stats about modules

from module import Module

class modmanage(Module):
    def __init__(self, scrap):
        super(modmanage, self).__init__(scrap)

        scrap.register_event("modmanage", "msg", self.distribute)

        # Modload
        self.register_cmd("modload", self.modload_cmd)
        self.register_cmd("load", self.modload_cmd)
        self.register_cmd("loadmod", self.modload_cmd)

        # Modunload
        self.register_cmd("modunload", self.modunload_cmd)
        self.register_cmd("unload", self.modunload_cmd)
        self.register_cmd("unloadmod", self.modunload_cmd)

        # Modlist
        self.register_cmd("modlist", self.modlist_cmd)

        # Getevents
        self.register_cmd("getevents", self.getevents_cmd)

    def annoy(self, server, bot):
        c = server["connection"]
        c.privmsg("#scrappy", "Tick.")

    def modload_cmd(self, server, event, bot):
        """modload - Loads a module"""
        c = server["connection"]

        param = event.cmd.split(" ")[1]
        msg = ""
        try:
            bot.load_module(param)
            msg = "%s loaded." % param
        except Exception as err:
            msg = "Unable to load %s." % param

        c.privmsg(event.target, msg)

    def modunload_cmd(self, server, event, bot):
        """modunload - Unloads a module"""
        c = server["connection"]

        param = event.cmd.split(" ")[1]
        if not param == "modmanage":
            msg = ""
            if bot.unload_module(param):
                msg = "Module '%s' unloaded successfully." % param
            else:
                msg = "Module '%s' failed to unload." % param
            c.privmsg(event.target, msg)
        else:
            c.privmsg(event.target, "You don't want to modmanage.")

    def modlist_cmd(self, server, event, bot):
        """modlist - Lists loaded modules"""
        c = server["connection"]

        msg = ", ".join(bot.modules)
        # TODO: Do I need to split? Or will irclib split long messages automatically.
        c.privmsg(event.target, msg)

    def getevents_cmd(self, server, event, bot):
        c = server["connection"]
        param = event.cmd.split(" ")[1]

        if param in bot.events:
            event_dict = bot.events[param]
            if len(event_dict) > 0:
                for module, callbacks in event_dict.items():
                    msg = []
                    for callback in callbacks:
                        msg.append(callback.__name__)

                    msg = ", ".join(msg)
                    c.privmsg(event.target, "%s: %s" % (module, msg))
            else:
                c.privmsg(event.target, "No callbacks registered for %s event" % param)
        else:
            c.privmsg(event.target, "%s not a valid event." % param)
