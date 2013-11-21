#default starting list of insults for insults.py
#run 'python insultdb.py' to create a new (or overwrite the old) insult database from this list

insults = { 
	'adjectives' : [
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
	],
		
	'bodyparts' : [
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
	],
		
	'professions' : [
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
	],
}

if __name__ == "__main__":
	import shelve
	
	try:
		insultdb = shelve.open('insultdb', writeback=True)
		insultdb.update(insults)
	except e:
		print "Error opening insultdb file:"+e
	insultdb.close()
