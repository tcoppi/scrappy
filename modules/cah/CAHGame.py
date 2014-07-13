# Cards Against Humanity game engine

from cards import Deck, NoMoreCards

# GAME LOOP
# Deal
# Choose Czar
# Black card shown
# WAIT ON EVERYONE TO !cah select (via PM)
# Display combinations
# WAIT ON CZAR to !cah vote
# GOTO 1
class CAHGame(object):
    def __init__(self, server, channel):
        self.status = "Waiting for players to join"

        # Keep track of the current channel/server
        self.channel = channel
        self.server = server

        #flag to keep track of whether or not game is running
        self.running = True

        #list of active players in a game
        self.players = []

        #dummy with a small deck for testing.
        #replace with actual card loading from DB later
        self.deck = Deck()

        # Who is the current czar in self.players?
        # Starting at -1 so the first iteration has the czar be the first person to join
        self.current_czar = -1

        # What is the current black card?
        self.current_card = None

        # Cards submitted
        self.submissions = {}

    #add a new player to the game
    def add_player(self, name):
        #check to see if player already in game
        if name in [p.name for p in self.players]:
            return False
        else:
            player = Player(name)
            self.players.append(player)
            self.deal(player)
            return player

    def get_player(self, name):
        players = [p for p in self.players if p.name == name]
        if len(players) == 1:
            return players[0]
        else:
            return None

    #start the game
    def start(self):
        self.status = "Waiting for player selection"
        new_card = self.deal_black()
        if new_card is None:
            self.message("Out of black cards! You played a long game!")
            #self.end()
            return
        czar = self.choose_czar()
        self.message("The new czar is %s" % czar.name)
        self.message("%s has drawn: %s" % (czar.name, self.current_card.body))
        for player in [player for player in self.players if player.name != czar.name]:
            self.message("You will need to choose \x02%d\x0F cards with the 'select X' command, where X is the card's position in your hand." % self.cards_needed, player)
            if self.cards_needed > 1:
                self.message("NOTE: To submit multiple cards, use the cah command 'select X Y ...', where the card numbers are separated by a space.", player)
            self.message("Ok, here's your hand:", player)
            for num, card in enumerate(player.hand):
                self.message("%d. %s" % (num+1, card.body), player)

    # Choose cards to play
    def select(self, player, cards):
        if self.status != "Waiting for player selection":
            self.message("This isn't your turn!", player)
            return
        if len(cards) != self.cards_needed:
            self.message("You need to play %d cards _only_" % self.cards_needed, player)
            return
        for card in cards:
            if card > len(player.hand) or card <= 0:
                self.message("You don't have a card %d in your hand!" % card, player)
                return
        self.submissions[player] = [player.hand[card-1] for card in cards]
        removed_cards = sorted(cards, reverse=True)
        for card in removed_cards:
            player.hand.pop(card-1)
        if len(self.submissions) == len(self.players)-1:
            self.display_selections()
            self.status = "Waiting for Czar vote"

    # Present the funnies
    def display_selections(self):
        self.message("Results are in!")
        if "_" not in self.current_card.body:
            self.message(self.current_card.body)
            for num, submission in enumerate(self.submissions.values()):
                self.message("%d. %s" % (num+1, submission[0].body))
        else:
            for num, submission in enumerate(self.submissions.values()):
                replacements = []
                filled_in = self.current_card.body.replace("_", "%s")
                for i in range(self.cards_needed):
                    replacements.append("\x02\x1F%s\x0F" % submission[i].body)
                filled_in = filled_in % tuple(replacements)
                self.message("%d. %s" % (num+1, filled_in))
        self.message("Now for %s to vote...." % self.players[self.current_czar].name)

    #deal cards to player until hand size is 10
    def deal(self, player):
        handSize = len(player.hand)
        
        while handSize < 10:
            player.hand.append(self.deck.draw("white"))
            handSize += 1
           
        return player.hand

    def choose_czar(self):
        self.current_czar = (self.current_czar + 1) % len(self.players)
        return self.players[self.current_czar]

    def deal_black(self):
        try:
            self.current_card = self.deck.draw("black")
            return self.current_card
        except NoMoreCards:
            return None

    def message(self, body, player=None):
        if player is not None:
            self.server.privmsg(player.name, body)
        else:
            self.server.privmsg(self.channel, body)

    @property
    def cards_needed(self):
        if "_" not in self.current_card.body:
            return 1
        else:
            return self.current_card.body.count("_")

#Utility class to manage Players
class Player(object):
    def __init__(self, name):
        self.name = name  #Player name (IRC nick)
        self.score = 0
        self.hand = []
        self.isCzar = False