import json
import logging
import threading
import time

import peewee
from ..dbmodel import DBModel


class Cache(DBModel):
    host = peewee.TextField()
    path = peewee.TextField()
    params = peewee.TextField()
    expires = peewee.IntegerField()
    xml = peewee.TextField()

class EveCache(object):
    db_lock = threading.Lock()

    def __init__(self):
        self.logger = logging.getLogger("scrappy.eve.cache")

        with self.db_lock:
            if not Cache.table_exists():
                Cache.create_table()

    def retrieve(self, host, path, params):
        params = json.dumps(params)
        self.logger.debug("Retrieving %s%s %s" % (host, path, params))

        cached = Cache.select().where(Cache.host==host, Cache.path==path, Cache.params==params)

        if cached.count() > 1:
            self.logger.debug("Cache Miss: Too many results.")
            return None
        else:
            try:
                cache_item = cached.get()
            except Cache.DoesNotExist:
                self.logger.debug("Cache Miss: No entry.")
                return None

            now = time.time()


            if now > cache_item.expires:
                self.logger.debug("Cache Miss: Entry has expired. (Currently: %d, Expired: %d)" % (now, cache_item.expires))
                return None
            else:
                self.logger.debug("Cache hit!")
                return cache_item.xml

    def store(self, host, path, params, doc, obj):

        if obj.cachedUntil-obj.currentTime > 0:
            with self.db_lock:

                params = json.dumps(params)

                self.logger.debug("Storing %s%s %s until %d." % (host, path, params, obj.cachedUntil))

                updated = Cache.update(expires=obj.cachedUntil, xml=doc).where(Cache.host==host, Cache.path==path, Cache.params==params)
                if updated.execute() == 0:
                    Cache(host=host, path=path, params=params, expires=obj.cachedUntil, xml=doc).save()


