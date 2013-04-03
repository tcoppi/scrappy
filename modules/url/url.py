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

        if len(event.arg) > 1:
            identifier = event.arg[0]
            url = event.arg[1]

            db[identifier] = url

            with open("urldb", "w") as fp:
                cPickle.dump(db, fp)

        elif len(event.arg) == 1:
            identifier = event.arg[0]
            if identifier in db:
                url = db[identifier]
            else:
                c.privmsg(event.target, "This URL isn't in the database!")
                return

        else:
            c.privmsg(event.target, "You need to have a url to look up or store!")
            return

        c.privmsg(event.target, url)
