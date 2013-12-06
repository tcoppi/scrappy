from time import sleep

from module import Module

class testmulti(Module):
    def __init__(self, scrap):
        super(testmulti, self).__init__(scrap)

        scrap.register_event("testmulti", "msg", self.distribute)

        self.register_cmd("testmulti", self.testmulti)
        self.register_cmd("testmulti", self.hailandon)
        self.register_cmd("testmulti", self.haiomega)
        self.register_cmd("testmulti", self.haicoppi)
        self.register_cmd("testmulti", self.sosleepy)

    def testmulti(self, server, event, bot):
        server.privmsg(event.source, "Sleeping for 5 seconds, yaaawn.")

    def haicoppi(self, server, event, bot):
        server.privmsg("tcoppi", "Ohai")

    def haiomega(self, server, event, bot):
        server.privmsg("[mharrison]", "Ohai")

    def hailandon(self, server, event, bot):
        server.privmsg("Landon", "Ohai")

    def sosleepy(self, server, event, bot):
        sleep(5)
        server.privmsg(event.target, "Yawn, I'm awake now!")

    def wtf(self):
        print "wtf!"
