# Eve API module

import eveapi.eveapi as eveapi

from module import Module

class eve(Module):
    def __init__(self, scrap):
        super(eve, self).__init__(scrap)

        scrap.register_event("eve", "msg", self.distribute)

        self.register_cmd("eve", self.eve)
        self.register_cmd("eve-add", self.eve_add)

    def setup_table(self, server):
        db_conn = self.get_db()
        # TODO: Could probably hash this, if there is no need to go from table->server/target again
        sql = "CREATE TABLE IF NOT EXISTS %s (name TEXT, id TEXT, key TEXT)" % server
        db_cursor = db_conn.cursor()
        db_cursor.execute(sql)
        db_conn.commit()
        db_conn.close()

    def eve(self, server, event, bot):
        """ List all characters right now """
        c = server["connection"]

        self.setup_table(server["servername"])
        db_conn = self.get_db()
        db_curs = db_conn.cursor()
        sql = "SELECT id, key FROM %s WHERE name=? " % server["servername"]
        db_curs.execute(sql, (event.nick,))

        credentials = db_curs.fetchone()
        db_conn.close()
        if credentials is None:
            c.privmsg(event.target, "%s isn't in the database, see the %seve-add command" % (event.nick, server["cmdchar"]))
            return

        (eve_id, eve_vcode) = credentials

        api = eveapi.EVEAPIConnection()
        auth = api.auth(keyID=eve_id, vCode=eve_vcode)
        result = auth.account.Characters()

        for character in result.characters:
            wallet = auth.char.AccountBalance(characterID=character.characterID)
            isk = wallet.accounts[0].balance
            c.privmsg(event.target, "Character: %s has %s ISK" % (character.name, isk))

    def eve_add(self, server, event, bot):
        """ Add account to eve using <ID> <VCODE> """
        c = server["connection"]

        tokens = event.cmd.split(" ")
        if len(tokens) < 3:
            c.privmsg(event.target, "Not enough arguments, <ID> and <VCODE> required.")
            return

        eve_id = tokens[1]
        eve_vcode = tokens[2]

        self.setup_table(server["servername"])
        db_conn = self.get_db()
        db_curs = db_conn.cursor()

        sql = "SELECT 1 FROM %s WHERE name=?" % server["servername"]
        db_curs.execute(sql, (event.nick,))
        if db_curs.fetchone() is None:
            sql = "INSERT INTO %s (name, id, key) VALUES (?, ?, ?)" % server["servername"]
            db_curs.execute(sql,(event.nick, eve_id, eve_vcode))
            c.privmsg(event.target, "Added %s to the database with ID %s" % (event.nick, eve_id))
        else:
            sql = "UPDATE %s SET id=?,key=? WHERE name=?" % server["servername"]
            db_curs.execute(sql, (eve_id, eve_vcode, event.nick))
            c.privmsg(event.target, "Updated %s in the database to ID %s" % (event.nick, eve_id))

        db_conn.commit()
        db_conn.close()
