import peewee

from dbmodel import DBModel
from user import Account

class Wallet(DBModel):
    # TODO: users will get an empty Account when they're first seen that will then be merged in to a new account when they authenticate (either associate User with an existing account that matches authentication or create a new account for it)
    acct = peewee.ForeignKeyField(Account, related_name='wallets')
    balance = peewee.DecimalField(max_digits=20, decimal_places=6, default=0.0)
