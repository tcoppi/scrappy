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
		
		usage = "start, join, end, add <black|white> <body>, select <1 2 ... N>,"

		if len(event.tokens) >= 2:
			arg = event.arg[0]
			msg = event.arg[1:]
			
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
					
			elif arg == "select":
				if len(msg) >= 1:
					cards = msg[0:]
					self.cah_select(server, event, bot, cards)
				else:
					usage = "Select card usage"
					server.privmsg(event.target, usage)
					
			elif arg == "vote":
				if len(msg) == 1:
					#going to need some args here
					self.cah_vote(server, event, bot, msg[0])
				else:
					usage = "Vote usage"
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
		
	def cah_select(self, server, event, bot, cards):
		'''Select card(s) to play from your hand.'''
		server.privmsg(event.target, "PLACEHOLDER: selecting cards %s" % ', '.join(cards))
		
	def cah_vote(self, server, event, bot, voted):
		'''Czar voting for group #.'''
		server.privmsg(event.target, "PLACEHOLDER: czar is voting for %s" % voted)
