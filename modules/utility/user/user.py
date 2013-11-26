import peewee
import json


from dbmodel import DBModel

class Account(DBModel):
    identifier = peewee.TextField()
    auth_service = peewee.TextField()
    name = peewee.TextField()

class User(DBModel):
    user = peewee.TextField()
    host = peewee.TextField()
    server = peewee.TextField()
    acct = peewee.ForeignKeyField(Account, related_name='users', null=True)


def is_authenticated(nickmask, servername):
    return get_account(nickmask, servername) is not None

def get_account(nickmask, servername):
    try:
        acct = User.get(User.user == nickmask.user, User.host == nickmask.host, User.server == servername)
        return acct
    except User.DoesNotExist:
        return None


