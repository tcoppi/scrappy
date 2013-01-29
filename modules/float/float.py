#Module for scrappy that implements floating-point functions
#originally thats what it was for, now it does a bunch more things

import sys
import struct
import binascii

def init(scrap):
	#register commands
	scrap.register_event("msg", float_cmd)
	scrap.register_event("msg", bs_cmd)

def float_cmd(server,list,bot):
    c = server["connection"]
    """"""

    cmd = list[4].split(" ")[0]

    if cmd == "$" and list[4].split(" ")[1]:

	try:
	   num = float(list[4].split(" ")[1])
	except ValueError:
	    try:
		num = int(list[4].split(" ")[1], 16)
	    except ValueError:
		c.privmsg(list[5],("%s: Invalid number") % list[0])
		return

	tmp = struct.pack("!f", num)
	tmp1 = struct.pack("!i", num)
	tmp2 = struct.pack("!d", num)
	tmp3 = struct.pack("!q", num)

	c.privmsg(list[5],("%s: 32bit float:0x%s | 2's complement int: 0x%s | 64bit float:0x%s | 2's complement long: 0x%s" % \
		(list[0],binascii.hexlify(tmp),binascii.hexlify(tmp1),binascii.hexlify(tmp2),binascii.hexlify(tmp3))))

def bs_cmd(server,list,bot):
    c = server["connection"]
    """"""

    cmd = list[4].split(" ")[0]

    if cmd == "bs" and list[4].split(" ")[1]:

	try:
	    num = int(list[4].split(" ")[1])
	except ValueError:
	    try:
		num = int(list[4].split(" ")[1], 16)
	    except ValueError:
		c.privmsg(list[5],("%s: Invalid number") % list[0])
		return

        tmp = struct.pack("<i", num)

	c.privmsg(list[5],("%s: 0x%s" % (list[0],binascii.hexlify(tmp))))
