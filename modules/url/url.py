import socket
import cPickle

from module import Module

class url(Module):
    def __init__(self, scrap):
        super(url, self).__init__(scrap)
        scrap.register_event("url", "msg", self.distribute)

        self.register_cmd("url", self.url)

    def url(self, server, event, bot):
        c = server["connection"]


        try:
            with open("urldb", "r+") as fp:
                db = cPickle.load(fp)
        except:
            db = {}

        params = event.cmd.split(" ")[1:]
        if len(params) > 1:
            identifier = params[0]
            url = params[1]

            db[identifier] = url

            with open("urldb", "w") as fp:
                cPickle.dump(db, fp)

        elif len(params) == 1:
            identifier = params[0]
            url = db[identifier]

        else:
            c.privmsg(event.target, "You need to have a url to look up or store!")
            return

        c.privmsg(event.target, url)
