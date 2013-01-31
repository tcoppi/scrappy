import socket

from module import Module

class dns(Module):
    def __init__(self, scrap):
        super(dns, self).__init__(scrap)

        scrap.register_event("dns", "msg", self.distribute)

        # Dns
        self.register_cmd("dns", self.dns)

    def dns(self, server, event, bot):
        c = server["connection"]
        param = event.cmd.split(" ")[1:]
        print param
        if len(param) == 0:
            msg = "Nothing to look up, zoob!"
        else:
            addr = param[0]
            if addr[-1].isdigit():
                try:
                    host, alias, ip = socket.gethostbyaddr(addr)
                    msg = "%s -> %s" % (addr, host)
                except socket.gaierror:
                    msg = "No result for '%s'" % addr
            else:
                try:
                    msg = "%s -> %s" % (addr, socket.gethostbyname(addr))
                except socket.gaierror:
                    msg = "No result for '%s'" % addr
            c.privmsg(event.target, msg)
