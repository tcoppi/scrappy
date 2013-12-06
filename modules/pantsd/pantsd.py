from module import Module, DBModel

from utility.user.user import get_account, Account

import peewee

class Pants(DBModel):
    status = peewee.BooleanField()
    acct = peewee.ForeignKeyField(Account, related_name='pants')

class pantsd(Module):
    models = [Pants]

    def __init__(self, scrap):
        super(pantsd, self).__init__(scrap)
        scrap.register_event("pantsd", "msg", self.distribute)

        self.register_cmd("pants", self.pants)

    def pants(self, server, event, bot):

        acct = get_account(event.source, server.server_name)
        if acct == None:
            server.privmsg(event.target, "%s, sorry, but you don't have an account." % event.source.nick)
            return
        if len(event.arg) > 0:
            status = event.arg[0].lower()
            if status not in ("on","off"):
                server.privmsg(event.target, "%s, your pants can either be \x02on\x02 or \x02off\x02." % event.source.nick)
                return

            if status == "on":
                server.privmsg(event.target, "%s, I see you put your pants on." % event.source.nick)
            else:
                server.privmsg(event.target, "%s, I see you took your pants off." % event.source.nick)

            q = Pants.update(status=(status=="on")).where(Pants.acct == acct)
            if q.execute() == 0:
                Pants(status=(status=="on"), acct=acct).save()

        else:
            try:
                acct_pants = Pants.get(Pants.acct == acct)
                if acct_pants.status:
                    server.privmsg(event.target, "%s, your pants are on!" % event.source.nick)
                else:
                    server.privmsg(event.target, "%s, your pants are off!" % event.source.nick)
            except Pants.DoesNotExist:
                server.privmsg(event.target, "%s, I don't know whether your pants are on or off!" % event.source.nick)
