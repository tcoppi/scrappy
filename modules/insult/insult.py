#insult mod via http://i.imgur.com/dXCGBE0.png
#see file insultdb.py for creating the initial insult database

from random import randint
import shelve
import threading

from module import Module

class insult(Module):
	def __init__(self, scrap):
		super(insult, self).__init__(scrap)

		self.lock = threading.Lock()

		self.insults = {}
		self.open_insultdb()

		scrap.register_event("insult", "msg", self.distribute)
		self.register_cmd("insult", self.insult_me)

	#opens the insultdb file using shelve
	def open_insultdb(self, dbfile = 'insultdb'):
		with self.lock:
			try:
				#open the file and store the insultdb to self.insults as dict
				insultdb = shelve.open("modules/insult/%s" % dbfile)
				self.insults.update(insultdb)
				insultdb.close()
			except Exception:
				self.logging.debug("Error reading insultdb file:" + Exception)
				return

	def add_insult(self, part, word):
		with self.lock:
			self.insults[part].append(word)
		self.save_insultdb()

	def del_insult(self, part, word):
		with self.lock:
			try:
				self.insults[part].remove(word)
			except:
				#didn't have that insult, nothing to do
				return
		self.save_insultdb()

	def save_insultdb(self, dbfile = 'insultdb'):
		with self.lock:
			try:
				#open the file and store self.insults
				insultdb = shelve.open("modules/insult/%s" % dbfile)
				insultdb.update(self.insults)
				insultdb.close()
			except Exception:
				self.logging.debug("Error reading insultdb file:" + Exception)
				return

	def insult_me(self, server, event, bot):
		'''Usage: "insult [-p | -add (adjective|bodypart|profession) word | -del (adjective|bodypart|profession) word] [foo]" where foo is someone/thing to insult.  Leave blank to make the bot insult yourself.'''
		#save the lengths of each insult component list
		a = len(self.insults['adjectives'])
		b = len(self.insults['bodyparts'])
		p = len(self.insults['professions'])

		#select a random word from each insult component
		adjective = self.insults['adjectives'][randint(0, a-1)]
		bodypart = self.insults['bodyparts'][randint(0, b-1)]
		profession = self.insults['professions'][randint(0, p-1)]

		#insert a/an if adjective starts with a consonant/vowel
		if adjective[0] in 'aeiou':
			adjective = "an %s" % adjective
		else:
			adjective = "a %s" % adjective

		#check for '-p' or 'word(s)' passed to insult
		if len(event.tokens) >= 2:
			arg = event.tokens[1]
			msg = event.tokens[2:]

			#return number of possible insult combinations if -p flag is given
			if arg == "-p":
				possible = a*b*p
				insult = "I know %d adjectives, %d bodyparts, and %d professions for a total of %d possible insult combinations!" % (a, b, p, possible)

			#add a new word to the db
			elif arg == "-add":
				if len(msg) < 2:
					insult = "Usage: insult -add (adjective|bodypart|profession) word"
				else:
					part = msg[0]+'s'
					word = ' '.join(msg[1:])

					if part in self.insults.keys():
						self.add_insult(part, word)
						insult = "Successfully added \"%s\" to %s." % (word, part)
					else:
						insult = "Error: \"%s\" is not a valid insult part.  Try one of the following: %s." % (part, ', '.join(self.insults.keys()))

			#delete a word from the db
			elif arg == "-del":
				if len(msg) < 2:
					insult = "Usage: insult -del (adjective|bodypart|profession) word"
				else:
					part = msg[0]+'s'
					word = ' '.join(msg[1:])

					if part in self.insults.keys():
						self.del_insult(part, word)
						insult = "Successfully deleted \"%s\" from %s." % (word, part)
					else:
						insult = "Error: \"%s\" is not a valid insult part.  Try one of the following: %s." % (part, ', '.join(self.insults.keys()))


			#no flag given, but a word or words was given, so insult word(s), stripping extra spaces
			else:
				insult = "%s is %s %s %s!" % (' '.join(event.tokens[1:]).strip(), adjective, bodypart, profession)

		#no arguments given so insult the user
		else:
			insult = "%s, you're %s %s %s!" % (event.source.nick, adjective, bodypart, profession)


		server.privmsg(event.target, insult)

