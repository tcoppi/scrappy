#CARDS AGAINST HUMANITY!

import threading
from module import Module

class cah(Module):
	def __init__(self, scrap):
		super(cah, self).__init__(scrap)
		
		self.lock = threading.Lock()
			
			
		scrap.register_event("cah", "msg", self.distribute)
		# but how do you handle commands for privmsg?
		#scrap.register_event("cah", "privmsg", self.distribute)
		self.register_cmd("cah", self.cah)
		
		
	def cah(self, server, event, bot):
		'''Main command to parse arguments to !cah trigger.'''
		
		usage = "Usage goes here"
		
		if len(event.tokens) >= 2:
			arg = event.tokens[1]
			msg = event.tokens[2:]
			
			if arg == "start":
				self.cah_start(server, event, bot)
				
			elif arg == "join":
				self.cah_join(server, event, bot)
				
			elif arg == "end":
				self.cah_end(server, event, bot)
				
			elif arg == "add":
				if len(msg) >= 2:
					color = msg[0]
					body = ' '.join(msg[1:])
					self.cah_add(server, event, bot, color, body)
				else:
					usage = "Add card usage"
					server.privmsg(event.target, usage)
			
		else:
			server.privmsg(event.target, usage)
			
################################################################################
# Function prototypes to fill in
################################################################################

	def cah_start(self, server, event, bot):
		'''Start a new game.'''
		server.privmsg(event.target, "PLACEHOLDER: starting new game")
		
	def cah_join(self, server, event, bot):
		'''Join the current game.'''
		server.privmsg(event.target, "PLACEHOLDER: joining the game")
		
	def cah_end(self, server, event, bot):
		'''Abort the current game.'''
		server.privmsg(event.target, "PLACEHOLDER: aborting the game")
		
	def cah_add(self, server, event, bot, color, body):
		'''Add a card to the database.'''
		server.privmsg(event.target, "PLACEHOLDER: adding %s card: %s" % (color, body))
