from time import sleep

def init(scrap):
	scrap.register_event("msg", testmulti)
	scrap.register_event("msg", haiomega)
	scrap.register_event("msg", sosleepy)
#	scrap.register_msg_event(haiomega)
#	scrap.register_msg_event(hailandon)
#	scrap.register_msg_event(sosleepy)


def testmulti(server, list, bot):
    c = server["connection"]
	cmd = list[4].split(" ")[0]
	if cmd == "testmulti":
		c.privmsg(list[5], "Sleeping for 5 seconds, yaaawn.")

def haicoppi(server, list, bot):
    c = server["connection"]
	cmd = list[4].split(" ")[0]
	if cmd == "testmulti":
		c.privmsg("tcoppi", "Ohai")

def haiomega(server, list, bot):
    c = server["connection"]
	cmd = list[4].split(" ")[0]
	if cmd == "testmulti":
		c.privmsg("[mharrison]", "Ohai")

def hailandon(server, list, bot):
    c = server["connection"]
	cmd = list[4].split(" ")[0]
	if cmd == "testmulti":
		c.privmsg("Landon", "Ohai")

def sosleepy(server, list, bot):
    c = server["connection"]
	cmd = list[4].split(" ")[0]
	if cmd == "testmulti":
		sleep(5)
		c.privmsg(list[5], "Yawn, I'm awake now!")

def wtf():
	print "wtf!"
