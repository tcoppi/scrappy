import asyncio
import string

letter = string.ascii_letters
number = string.digits
special = "-[]\\`^{}"

# http://tools.ietf.org/html/rfc1459#section-2.3
class Message(object):
    encoding="utf8"
    def __init__(self, command, parameters, prefix=None):
        # FIXME
        #assert(command in COMMAND_LIST)
        self.command = command
        self.parameters = parameters
        self.prefix = prefix

    @classmethod
    def parse(cls, message : bytes):
        message = message.rstrip(b'\r\n') # strip \r\n
        l,_,r = message.partition(b' ')

        if l.startswith(b':'):
            prefix = l[1:]
            l,_,r = r.partition(b' ')
            command = l
        else:
            prefix = None
            command = l

        params = []
        l,_,r = r.partition(b' ')
        while l:
            if l.startswith(b':'):
                params.append(b''.join([l[1:],_,r]))
                break
            else:
                params.append(l)
                l,_,r = r.partition(b' ')

        command = str(command, cls.encoding)
        params = [str(param, cls.encoding) for param in params]
        if prefix is not None:
            prefix = str(prefix, cls.encoding)
        return cls(command, params, prefix)

    def format(self):
        parts = []

        if self.prefix is not None:
            parts.append(":{}".format(self.prefix))
        parts.append(self.command)
        parts.extend(self.parameters[:-1])
        if " " in self.parameters[-1]:
            parts.append(":{}".format(self.parameters[-1]))
        else:
            parts.append(self.parameters[-1])
        msg = " ".join(parts)+"\r\n"
        byte_msg = bytearray(msg,encoding="utf8")

        #FIXME
        assert(len(byte_msg) < 512)
        return byte_msg

    def __repr__(self):
        ret = ""
        if self.prefix:
            ret += "prefix: {}\n".format(self.prefix)
        ret += "command: {}\n".format(self.command)
        if self.parameters:
            ret += "parameters: {}".format(", ".join(x for x in self.parameters))
        return ret

class Connection(object):

    def __init__(self, host, port, ssl):
        self._conn = asyncio.open_connection(host=host, port=port, ssl=ssl)

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from self._conn
        self._conn = None
        a = Message("NICK", ["ScrapTest"])
        b = Message("USER", ["Scrapper", "scrapperhost", "server", "Scrap Bot"])
        self.writer.write(a.format())
        self.writer.write(b.format())
        yield from self.writer.drain()


        while True:
            a = yield from self.reader.readline()
            if len(a) == 0:
                self.writer.close()
                return
            msg = Message.parse(a)
            if hasattr(self, "on_any"):
                meth = getattr(self, "on_any")
                if asyncio.iscoroutine(meth) or asyncio.iscoroutinefunction(meth):
                    yield from meth(msg)
                else:
                    meth(msg)
            if hasattr(self, "on_{}".format(msg.command.lower())):
                meth = getattr(self, "on_{}".format(msg.command.lower()))
                if asyncio.iscoroutine(meth) or asyncio.iscoroutinefunction(meth):
                    yield from meth(msg)
                else:
                    meth(msg)

    @asyncio.coroutine
    def on_any(self, msg):
        print(msg)

    @asyncio.coroutine
    def on_ping(self, msg):
        reply = Message("PONG", msg.parameters)
        yield from self.send(reply)

    @asyncio.coroutine
    def send(self, msg):
        self.writer.write(msg.format())
        print(msg.format())
        yield from self.writer.drain()

