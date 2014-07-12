# Cards Against Humanity game engine

from cards import Deck, NoMoreCards


class CAHGame:
    def __init__(self):
        self.status = "Loaded CAHGame."

        #flag to keep track of whether or not game is running
        self.running = False

        #list of active players in a game
        self.players = []

        #dummy with a small deck for testing.
        #replace with actual card loading from DB later
        self.deck = Deck()

        # Keep track of the current channel
        self.channel = ""

    #add a new player to the game
    def add_player(self, name):
        self.players.append(Player(name))

    #start the game
    def start(self):
        pass


#Utility class to manage Players
class Player:
    def __init__(self, name):
        self.name = name  #Player name (IRC nick)
        self.score = 0
        self.hand = {}
        self.isCzar = False