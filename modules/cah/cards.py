from module import DBModel

import peewee

class Cards(DBModel):
    color = peewee.TextField()
    body = peewee.TextField()


