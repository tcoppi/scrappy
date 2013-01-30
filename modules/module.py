class Module(object):
    def __init__(self, scrap):
        self.command_callbacks = {}

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


