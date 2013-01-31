#Module for scrappy that implements floating-point functions
#originally thats what it was for, now it does a bunch more things

import sys
import struct
import binascii

from module import Module

class floatmod(Module):
    def __init__(self, scrap):
        super(floatmod, self).__init__(scrap)

        scrap.register_event("floatmod", "msg", self.distribute)

        self.register_cmd("$", self.float_cmd)
        self.register_cmd("bs", self.bs_cmd)

    def float_cmd(self, server, event, bot):
        c = server["connection"]
        """"""

        param = event.cmd.split(" ")[1]

        try:
            num = float(param)
        except ValueError:
            try:
                num = int(param, 16)
            except ValueError:
                c.privmsg(event.target,("%s: Invalid number") % param)
                return

        tmp = struct.pack("!f", num)
        tmp1 = struct.pack("!i", num)
        tmp2 = struct.pack("!d", num)
        tmp3 = struct.pack("!q", num)

        c.privmsg(event.target,("%s: 32bit float:0x%s | 2's complement int: 0x%s | 64bit float:0x%s | 2's complement long: 0x%s" % \
            (param,binascii.hexlify(tmp),binascii.hexlify(tmp1),binascii.hexlify(tmp2),binascii.hexlify(tmp3))))

    def bs_cmd(self, server, event, bot):
        """"""

        c = server["connection"]

        param = event.cmd.split(" ")[1]

        try:
            num = int(param)
        except ValueError:
            try:
                num = int(param, 16)
            except ValueError:
                c.privmsg(event.target,("%s: Invalid number") % param)
                return

        tmp = struct.pack("<i", num)

        c.privmsg(event.target,("%s: 0x%s" % (param,binascii.hexlify(tmp))))
