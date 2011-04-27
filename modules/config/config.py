# Module that implements config file functionality for scrap

import sys

def init(scrap):
	#hardcoded for now
	scrap.server = "thisnukes4u.net"
	scrap.cmdchar = "!"
	scrap.nickname = "scrappy"
	scrap.username = "scrappy"
	scrap.realname = "Scrappy Bot"
	scrap.port = 6697
	scrap.chanlist = ["#scrappy"]
	
	#modules to load on startup
	scrap.startup = []
	
	print "THIS SHOULD NOT WORK"
	
