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
		connection = server["connection"]
		
		adjective = self.adjectives[randint(0, len(self.adjectives)-1)]
		bodypart = self.bodyparts[randint(0, len(self.bodyparts)-1)]
		profession = self.professions[randint(0, len(self.professions)-1)]
		
		insult = "%s, you're a(n) %s %s %s!" % (event.source.nick, adjective, bodypart, profession)
		
		print insult
		
		connection.privmsg(event.target, insult)
		
