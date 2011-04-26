

def init(scrap):
	scrap.register_event("msg", reverse)
	
	
def reverse(c, args, bot):
	"""Takes a string and reverses it.  Simple."""
	cmd = args[4].split(" ")[0]
	if cmd == "reverse":
		
		if not args[4].split(" ")[1:]:
			strng = "?tahw esreveR"
		else:
			strng = args[4].replace(cmd, "")
			#print strng
			rev = list(strng)
			rev.reverse()
			strng = ''.join(rev)
			
		
		c.privmsg(args[5], strng)
