#karma module for scrappy

import re

plusexp = re.compile('\+\+$')
minusexp = re.compile('\-\-$')

#this needs to be stored in sql or a text file or something
karma = {}

def init(scrap):
	scrap.register_event("msg", karma_look)
	scrap.register_event("msg", karma_cmd)

def karma_look(c,list,bot):
	""" Should not be called directly """
	nick = list[0]
	if list[3] == False:
		if plusexp.search(list[4]):
			name = list[4].split("++")[0]
			newname = name.lower()
			if newname == nick.lower():
				c.privmsg(list[5], "No touching yourself, %s." % nick)
				return
			try:
				karma[newname] = karma[newname] + 1
			except KeyError:
				karma[newname] = 1

			c.privmsg(list[5],"%s karma increased to %s" %
					(name,karma[newname]))
	if minusexp.search(list[4]):
			name = list[4].split("--")[0]
			newname = name.lower()
			if newname == nick.lower():
				c.privmsg(list[5], "No touching yourself, %s." % nick)
				return
			try:
				karma[newname] = karma[newname] - 1
			except KeyError:
				karma[newname] = -1

			c.privmsg(list[5],"%s karma decreased to %s" %
					(name,karma[newname]))

def karma_cmd(c,list,bot):
	""" Tells the karma of the argument. """
	cmd = list[4].split(" ")[0]

	if list[3] and cmd == "karma":
		name = list[4].split(" ")[1]
		newname = name.lower()
		
		try:
			karma[newname] = karma[newname]
		except KeyError:
			c.privmsg(list[5],"%s is not in the karma database." %
					name)
			return

		c.privmsg(list[5],"%s karma is %s" % (name,karma[newname]))

