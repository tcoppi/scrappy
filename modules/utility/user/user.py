import peewee
import json

from dbmodel import DBModel

class Account(DBModel):
    identifier = peewee.TextField()
    name = peewee.TextField()

# An account can have many auth backends
class AuthBackend(DBModel):
    identifier = peewee.TextField()
    auth_service = peewee.TextField()
    acct = peewee.ForeignKeyField(Account, related_name='backends')

# Similarly, many users can be attached to an account
class User(DBModel):
    user = peewee.TextField()
    host = peewee.TextField()
    server = peewee.TextField()
    acct = peewee.ForeignKeyField(Account, related_name='users')

def is_authenticated(user, servername):
    acct = get_account(user, servername)
    nondummy_auth = AuthBackend.select().where(AuthBackend.acct == acct, AuthBackend.auth_service != "dummy").count()
    return nondummy_auth > 0

def get_user(user, servername):
    try:
        user = User.get(User.user == user.nick, User.host == user.host, User.server == servername)
    except User.DoesNotExist:
        acct = Account(identifier=str(user), name=user.nick)
        acct.save()
        auth_backend = AuthBackend(identifier=str(user), auth_service="dummy", acct=acct)
        auth_backend.save()
        user = User(user=user.nick, host=user.host, server=servername, acct=acct)
        user.save()

    return user

def get_account(user, servername):
    user_obj = get_user(user, servername)
    return user_obj.acct

def merge_accounts(from_acct, to_acct):
    backends = AuthBackend.select().where(AuthBackend.acct == from_acct)
    users = User.select().where(User.acct == from_acct)

    for backend in backends:
        backend.acct = to_acct

    for user in users:
        user.acct = to_acct
