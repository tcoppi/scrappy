import decimal

from module import Module, DBModel

from utility.user.user import get_account
from utility.user.wallet import Wallet

class wallet(Module):
    models = [Wallet]

    def __init__(self, scrap):
        super(wallet, self).__init__(scrap)
        scrap.register_event("fact", "msg", self.distribute)

        self.register_cmd("wallet", self.wallet_amt)
        self.register_cmd("transfer", self.transfer)
        self.register_cmd("gimme", self.gimme)

    def get_wallet(self, nick, server_name):
        acct = get_account(nick, server_name)
        try:
            user_wallet = Wallet.get(Wallet.acct == acct)
        except Wallet.DoesNotExist:
            user_wallet = Wallet(acct = acct)
            user_wallet.save()

        return user_wallet

    def transfer(self, server, event, bot):
        user_wallet = self.get_wallet(event.source, server.server_name)

        server.privmsg(event.target, "Send to %s" % event.args[0])

        server.privmsg(event.target, "Error! Not yet implemented because scrappy doesn't know who's who, except for who's talking!")


    def wallet_amt(self, server, event, bot):
        user_wallet = self.get_wallet(event.source, server.server_name)

        server.privmsg(event.target, "Your wallet balance is %.6f" % user_wallet.balance)

    def gimme(self, server, event, bot):
        user_wallet = self.get_wallet(event.source, server.server_name)

        user_wallet.balance += decimal.Decimal(.01)
        user_wallet.save()
