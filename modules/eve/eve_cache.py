import json
import logging
import sqlite3
import threading
import time

class EveCache(object):
    db_lock = threading.Lock()

    def __init__(self):

        self.logger = logging.getLogger("scrappy.eve.cache")

        with self.db_lock:
            conn = sqlite3.connect('db/eve_cache.db')
            cursor = conn.cursor()
            sql = "CREATE TABLE IF NOT EXISTS eve_cache (host TEXT, path TEXT, params TEXT, expires INTEGER, xml TEXT)"
            cursor.execute(sql)
            sql = "CREATE INDEX IF NOT EXISTS eve_cache_idx ON eve_cache (host, path, params)"
            cursor.execute(sql)
            conn.commit()
            conn.close()

    def retrieve(self, host, path, params):
        conn = sqlite3.connect('db/eve_cache.db')
        params = json.dumps(params)
        self.logger.debug("Retrieving %s%s %s" % (host, path, params))
        sql = "SELECT xml, expires FROM eve_cache WHERE host=? AND path=? AND params=?"
        cursor = conn.cursor()
        cursor.execute(sql, (host, path, params))
        rows = cursor.fetchall()
        conn.close()

        if len(rows) > 1:
            self.logger.debug("Cache Miss: Too many results.")
            return None
        elif len(rows) < 1:
            self.logger.debug("Cache Miss: No entry.")
            return None
        else:
            cache = rows[0]
            now = time.time()
            xml = cache[0]
            expires = int(cache[1])

            if now > expires:
                self.logger.debug("Cache Miss: Entry has expired. (Currently: %d, Expired: %d)" % (now, expires))
                return None
            else:
                self.logger.debug("Cache hit!")
                return xml

    def store(self, host, path, params, doc, obj):

        if obj.cachedUntil-obj.currentTime > 0:
            with self.db_lock:
                conn = sqlite3.connect('db/eve_cache.db')

                params = json.dumps(params)

                self.logger.debug("Storing %s%s %s until %d." % (host, path, params, obj.cachedUntil))
                cursor = conn.cursor()
                # Ouch. Nuking anything existing due to threading issues.
                sql = "DELETE FROM eve_cache WHERE host=? AND path=? AND params=?"
                cursor.execute(sql, (host, path, params))
                sql = "INSERT INTO eve_cache (host, path, params, expires, xml) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (host, path, params, obj.cachedUntil, doc))

                conn.commit()
                conn.close()


