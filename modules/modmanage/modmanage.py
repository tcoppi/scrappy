#stuff for loading/unloading/managing/getting stats about modules

def init(scrap):
	scrap.register_event("modmanage", "msg", modload_cmd)
	scrap.register_event("modmanage", "msg", modunload_cmd)
	scrap.register_event("modmanage", "msg", modlist_cmd)
	scrap.register_event("modmanage", "msg", getevents_cmd)

def modload_cmd(c,list,bot):
	"""modload - Loads a module"""
	cmd = list[4].split(" ")[0]

	if (cmd == "modload") or (cmd =="load") or (cmd =="loadmod") and list[3]:
		param = list[4].split(" ")[1]
		c.privmsg(list[5], bot.load_module(param))
		
def modunload_cmd(c, list, bot):
	"""modunload - Unloads a module"""
	cmd = list[4].split(" ")[0]
	if (cmd == "modunload") or (cmd == "unload") or (cmd == "unloadmod") and list[3]:
		param = list[4].split(" ")[1]
		if not param == "modmanage":
			c.privmsg(list[5], bot.unload_module(param))
		else:
			c.privmsg(list[5], "Cannot unload modmanage.")

def modlist_cmd(c,list,bot):
	"""modlist - Lists loaded modules"""
	if list[4] == "modlist" and list[3]:
		c.privmsg(list[5],bot.modulelist)
		
def getevents_cmd(c, list, bot):
	cmd = list[4].split(" ")[0]
	if cmd == "getevents" and list[3]:
		param = list[4].split(" ")[1]
		param = "bot."+param+"_events"
		c.privmsg(list[5], eval(param))
