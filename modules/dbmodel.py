import peewee

class DBModel(peewee.Model):
    #TODO: hardcoded, tut
    class Meta:
        database = peewee.SqliteDatabase('scrappy.db', threadlocals=True)


