from module import Module, DBModel

import peewee

class Factoid(DBModel):
    phrase = peewee.TextField()
    factoid = peewee.TextField()

class fact(Module):
    models = [Factoid]

    def __init__(self, scrap):
        super(fact, self).__init__(scrap)
        scrap.register_event("fact", "msg", self.distribute)

        self.register_cmd("fact", self.fact)

    def fact(self, server, event, bot):

        if len(event.arg) > 1:
            phrase = event.arg[0]
            factoid = " ".join(event.arg[1:])
            q = Factoid.update(factoid=factoid).where(Factoid.phrase == phrase)
            if q.execute() == 0:
                Factoid(phrase=phrase, factoid=factoid).save()
            server.privmsg(event.target, "%s is %s" % (phrase, factoid))
        elif len(event.arg) == 1:
            phrase = event.arg[0]
            try:
                factoid = Factoid.get(Factoid.phrase == phrase)
                server.privmsg(event.target, factoid.factoid)
            except Factoid.DoesNotExist:
                server.privmsg(event.target, "Factoid %s does not exist." % phrase)
        else:
            server.privmsg(event.target, "You need to have a phrase to look up or store!")
