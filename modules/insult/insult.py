#insult mod via http://i.imgur.com/dXCGBE0.png

from random import randint

from module import Module

class insult(Module):
	def __init__(self, scrap):
		super(insult, self).__init__(scrap)
		
		self.adjectives = (
					'lazy',
					'stupid',
					'insecure',
					'idiotic',
					'slimy',
					'slutty',
					'smelly',
					'pompous',
					'communist',
					'dicknose',
					'pie-eating',
					'racist',
					'elitist',
					'white trash',
					'drug-loving',
					'butterface',
					'tone deaf',
					'ugly',
					'creepy',
		)
		
		self.bodyparts = (
					'douche',
					'ass',
					'turd',
					'rectum',
					'butt',
					'cock',
					'shit',
					'crotch',
					'bitch',
					'turd',
					'prick',
					'slut',
					'taint',
					'fuck',
					'dick',
					'boner',
					'shart',
					'nut',
					'sphincter',
		)
		
		self.professions = (
					'pilot',
					'canoe',
					'captain',
					'pirate',
					'hammer',
					'knob',
					'box',
					'jockey',
					'nazi',
					'waffle',
					'goblin',
					'blossom',
					'biscuit',
					'clown',
					'socket',
					'monster',
					'hound',
					'dragon',
					'balloon',
		)
		
		scrap.register_event("insult", "msg", self.distribute)
		self.register_cmd("insult", self.insult_me)
		
	def insult_me(self, server, event, bot):
		'''Usage: "insult [-p | foo]" where foo is someone/thing to insult.  Leave blank to make the bot insult yourself.'''
		connection = server["connection"]
		
		#save the lengths of each insult component list
		a = len(self.adjectives)
		b = len(self.bodyparts)
		p = len(self.professions)
		
		#select a random word from each insult component
		adjective = self.adjectives[randint(0, a-1)]
		bodypart = self.bodyparts[randint(0, b-1)]
		profession = self.professions[randint(0, p-1)]
		
		#check for '-p' or 'word(s)' passed to insult
		if len(event.tokens) >= 2:
			arg = event.tokens[1]
			
			#return number of possible insult combinations if -p flag is given
			if arg == "-p":
				possible = a*b*p
				insult = "I know %d adjectives, %d bodyparts, and %d professions for a total of %d possible insult combinations!" % (a, b, p, possible)
			
			#no flag given, but a word or words was given, so insult word(s), stripping extra spaces
			else:
				insult = "%s is a(n) %s %s %s!" % (' '.join(event.tokens[1:]).strip(), adjective, bodypart, profession)
				
		#no arguments given so insult the user
		else:
			insult = "%s, you're a(n) %s %s %s!" % (event.source.nick, adjective, bodypart, profession)
		
		
		connection.privmsg(event.target, insult)
		
