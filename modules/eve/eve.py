# Eve API module

import time

import eveapi.eveapi as eveapi

from module import Module

from eve_cache import EveCache

import peewee

class EVEAcct(peewee.Model):
    server = peewee.TextField()
    irc_name = peewee.TextField()
    eve_id = peewee.TextField()
    eve_vcode = peewee.TextField()

    class Meta:
        database = peewee.SqliteDatabase('db/%s.db' % __name__.split('.')[0], threadlocals=True)



class eve(Module):
    models = [EVEAcct]
    def __init__(self, scrap):
        super(eve, self).__init__(scrap)

        scrap.register_event("eve", "msg", self.distribute)

        self.register_cmd("eve-wallet", self.wallet)
        self.register_cmd("eve-skill", self.skill)
        self.register_cmd("eve-add", self.eve_add)

    def skill(self, server, event, bot):
        c = server["connection"]

        credentials = self.get_credentials(server["servername"], event.source.nick)
        if credentials is None:
            c.privmsg(event.target, "%s isn't in the database, see the %seve-add command" % (event.source.nick, server["cmdchar"]))
            return

        (eve_id, eve_vcode) = credentials

        api = eveapi.EVEAPIConnection(cacheHandler=EveCache())
        auth = api.auth(keyID=eve_id, vCode=eve_vcode)
        result = auth.account.Characters()

        skills = api.eve.SkillTree()

        for character in result.characters:
            c.privmsg(event.target, "Training queue for %s" % character.name)
            queue = auth.char.SkillQueue(characterID=character.characterID)
            for training_skill in queue.skillqueue:
                # Oh boy, this is going to be horrible.
                for group in skills.skillGroups:
                    for skill in group.skills:
                        if skill.typeID == training_skill.typeID:
                            time_str = time.strftime("%B %d %H:%M:%S Central",time.localtime(training_skill.endTime))
                            c.privmsg(event.target, "%s: %s to level %s. Ends %s." % (group.groupName, skill.typeName, training_skill.level, time_str))




    def wallet(self, server, event, bot):
        """ List all character wallets """
        c = server["connection"]

        credentials = self.get_credentials(server["servername"], event.source.nick)
        if credentials is None:
            c.privmsg(event.target, "%s isn't in the database, see the %seve-add command" % (event.source.nick, server["cmdchar"]))
            return

        (eve_id, eve_vcode) = credentials

        api = eveapi.EVEAPIConnection(cacheHandler=EveCache())
        auth = api.auth(keyID=eve_id, vCode=eve_vcode)
        result = auth.account.Characters()

        for character in result.characters:
            wallet = auth.char.AccountBalance(characterID=character.characterID)
            isk = wallet.accounts[0].balance
            c.privmsg(event.target, "Character: %s has %s ISK" % (character.name, isk))

    def eve_add(self, server, event, bot):
        """ Add account to eve using <ID> <VCODE> """
        c = server["connection"]

        if len(event.arg) < 2:
            c.privmsg(event.target, "Not enough arguments, <ID> and <VCODE> required.")
            return

        eve_id = event.tokens[1]
        eve_vcode = event.tokens[2]

        updated = EVEAcct.update(eve_id = eve_id, eve_vcode = eve_vcode).where(EVEAcct.server == server["servername"], EVEAcct.irc_name == event.source.nick)
        print updated.execute()
        if updated.execute() == 0:
            EVEAcct(server=server["servername"], irc_name=event.source.nick, eve_id=eve_id, eve_vcode=eve_vcode).save()

        c.privmsg(event.target, "Account added!")

    def get_credentials(self, server, nick):
        try:
            acct = EVEAcct.get(EVEAcct.server == server, EVEAcct.irc_name == nick)
            return (acct.eve_id, acct.eve_vcode)
        except EVEAcct.DoesNotExist:
            return None


