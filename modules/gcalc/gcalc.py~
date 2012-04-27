import socket

def init(bot):
	bot.register_event("dns", "msg", dns)
	
def dns(c, args, bot):
	cmd = args[4].split(" ")[0]
	if cmd == "dns":
		if not args[4].split(" ")[1:]:
			ret = "Nothing to look up, zoob!"
		else:
			ret = args[4].split(" ")[1]
			if ret[-1].isdigit():
				try:
					host, alias, ip = socket.gethostbyaddr(ret)
					ret = "%s -> %s" % (ret, host)
				except socket.gaierror:
					ret = "No result for '%s'" % ret
			else:
				try:
					ret = "%s -> %s" % (ret, socket.gethostbyname(ret))
				except socket.gaierror:
					ret = "No result for '%s'" % ret
			
		c.privmsg(args[5], ret)
