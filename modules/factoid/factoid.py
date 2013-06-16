import socket
import cPickle

from module import Module

class factoid(Module):
    def __init__(self, scrap):
        super(factoid, self).__init__(scrap)
        scrap.register_event("all", "msg", self.factoid)

#        self.register_cmd("url", self.url)

    def factoid(self, server, event, bot):
        c = server["connection"]
        event.tokens = event.arguments[0].split(" ")

        if not event.tokens or not event.tokens[0]:
            return

        cmdchar = event.tokens[0][0]
        if cmdchar != server["factoidchar"]:
            return

        event.factoid = event.tokens[0][1:]

        if event.factoid.split(" ")[1] == '=':
            # we are modifying a factoid
            self.change_factoid(event.factoid, event.factoid.split("=")[1])

        rf = self.lookup_factoid(event.factoid)
        pf = self.parse_factoid(rf)
        c.privmsg(event.target, pf)

    def change_factoid(self, factoid, new_value):
        pass

    def parse_factoid(self, raw_factoid):
        rep = raw_factoid.find(">")
        if rep != 0:
            return raw_factoid[rep + 1:]
        else:
            return raw_factoid

    def lookup_factoid(self, factoid):
        db = self.get_db()
        cur = db.cursor()

        cur.execute("select value from facts where name = \"%s\"" % factoid)

        rawfact = cur.fetchone()

        if not rawfact:
            return "Factoid not found."

        return rawfact[0]
