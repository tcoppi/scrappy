import asyncio
import ssl

from irc.rfc1459.connection import Connection
HOST=''

@asyncio.coroutine
def connect(host=HOST, use_ssl=True, port=6697):
    if use_ssl:
        use_ssl = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        use_ssl.verify_mode = ssl.CERT_NONE
    conn = Connection(host, port, use_ssl)
    yield from conn.connect()
    yield from asyncio.sleep(1)
    pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()

