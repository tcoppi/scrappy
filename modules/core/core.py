#Module for scrappy that implements some core commands, like 'help'

import sys

def init(scrap):
	#register commands
	scrap.register_event("core", "msg", help_cmd)
	scrap.register_event("core", "msg", join_cmd)

def help_cmd(c,list,bot):
	"""help - Lists all available commands and their docstrings"""
	if list[4] == "help" and list[3]:
		#put the events into a set so we can compute the union
		#Or maybe we should use sets for the events from the start?

		s1 = set()
		s2 = set()

		for event in bot.privmsg_events:
			s1.add(event.__doc__)
		for event in bot.pubmsg_events:
			s2.add(event.__doc__)

		funcnames = s1.union(s2)

		for name in funcnames:
			c.privmsg(list[0],name)

def join_cmd(c,list,bot):
    """join a channel"""
    cmd = list[4].split(" ")[0]

    #replace tcoppi with the name of the bot owner(config option)
    if cmd == "join" and list[0] == "tcoppi":
	chan = list[4].split(" ")[1]
	c.join(chan)

