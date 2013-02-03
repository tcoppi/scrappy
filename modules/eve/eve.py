# Eve API module

from module import Module

class eve(Module):
    def __init__(self, scrap):
        super(eve, self).__init__(scrap)

        scrap.register_event("eve", "msg", self.distribute)

        self.register_cmd("eve", self.eve)

    def eve(self, server, event, bot):
        c = server["connection"]
        c.privmsg(event.target, "Don't use this yet")
