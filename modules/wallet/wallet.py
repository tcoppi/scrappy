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

    def transfer(self, server, event, bot):
        c = server["connection"]
        acct = get_account(event.source, server["servername"])
        try:
            user_wallet = Wallet.get(Wallet.acct == acct)
        except Wallet.DoesNotExist:
            user_wallet = Wallet(acct = acct)
            user_wallet.save()

        c.privmsg(event.target, "Error! Not yet implemented because scrappy doesn't know who's who, except for who's talking!")


    def wallet_amt(self, server, event, bot):
        c = server["connection"]
        acct = get_account(event.source, server["servername"])
        try:
            user_wallet = Wallet.get(Wallet.acct == acct)
        except Wallet.DoesNotExist:
            user_wallet = Wallet(acct = acct)
            user_wallet.save()

        c.privmsg(event.target, "Your wallet balance is %.6f" % user_wallet.balance)
