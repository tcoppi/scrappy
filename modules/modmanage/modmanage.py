#stuff for loading/unloading/managing/getting stats about modules

class modmanage(object):
    def __init__(self, scrap):
        self.command_callbacks = {}
        scrap.register_event("modmanage", "msg", self.distribute)
        #scrap.register_event("modmanage", "msg", self.modload_cmd)
        #scrap.register_event("modmanage", "msg", self.modunload_cmd)
        #scrap.register_event("modmanage", "msg", self.modlist_cmd)
        #scrap.register_event("modmanage", "msg", self.getevents_cmd)
        self.register_cmd("modload", self.modload_cmd)
        self.register_cmd("load", self.modload_cmd)
        self.register_cmd("loadmod", self.modload_cmd)

    def register_cmd(self, cmd, callback):
        if cmd not in self.command_callbacks:
            self.command_callbacks[cmd] = []

        self.command_callbacks[cmd].append(callback)

    def distribute(self, server, list, bot):
        if list[3]: # event is command
            command = list[4].split(" ")[0]
            if command in self.command_callbacks:
                for callback in self.command_callbacks[command]:
                    callback(server, list, bot)


    def modload_cmd(self, server,list,bot):
        """modload - Loads a module"""
        c = server["connection"]

        param = list[4].split(" ")[1]
        c.privmsg(list[5], bot.load_module(param))

    def modunload_cmd(self, server, list, bot):
        """modunload - Unloads a module"""
        c = server["connection"]
        cmd = list[4].split(" ")[0]
        if (cmd == "modunload") or (cmd == "unload") or (cmd == "unloadmod") and list[3]:
            param = list[4].split(" ")[1]
            if not param == "modmanage":
                c.privmsg(list[5], bot.unload_module(param))
            else:
                c.privmsg(list[5], "Cannot unload modmanage.")

    def modlist_cmd(self, server,list,bot):
        """modlist - Lists loaded modules"""
        c = server["connection"]
        if list[4] == "modlist" and list[3]:
            c.privmsg(list[5],bot.modulelist)

    def getevents_cmd(self, server, list, bot):
        c = server["connection"]
        cmd = list[4].split(" ")[0]
        if cmd == "getevents" and list[3]:
            param = list[4].split(" ")[1]
            param = "bot."+param+"_events"
            c.privmsg(list[5], eval(param))
