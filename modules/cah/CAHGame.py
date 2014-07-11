#Cards Against Humanity game engine

class CAHGame:
	def __init__(self):
		
		self.status = "Loaded CAHGame."
		
		#flag to keep track of whether or not game is running
		self.running = False
		
		#list of active players in a game
		self.players = []
		
		#dummy with a small deck for testing.
		#replace with actual card loading from DB later
		self.deck ={
			'questions' : [
				"_? There's an app for that.",
				"I got 99 problems but _ ain't one.",
			],
			'answers' : [
				"Flying sex snakes.",
				"Michelle Obama's arms.",
				"German dungeon porn.",
				"White people.",
				"Getting so angry that you pop a boner.",
			]
		}
		
		
	#add a new player to the game
	def add_player(self, name):
		self.players.append(Player(name))
		



#Utility class to manage Players
class Player:
	def __init__(self, name):
		self.name = name.split('!')[0] #Player name (IRC nick)
		self.score = 0
		self.hand = {}
		self.isCzar = False
