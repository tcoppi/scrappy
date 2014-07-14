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
        # Reset back to the start
        self.status = "Waiting for player selection"
        self.submissions = {}

        # Refresh player hands
        for player in self.players:
            self.deal(player)

        # Deal the new black card
        new_card = self.deal_black()
        if new_card is None:
            self.message("Out of black cards! You played a long game!")
            #self.end() # TODO: make this end the game when out of black cards
            return

        czar = self.choose_czar()
        self.message("The new czar is %s" % czar.name)
        self.message("%s has drawn: %s" % (czar.name, self.current_card.body))

        # Show players their current hand
        for player in [player for player in self.players if player.name != czar.name]:
            self.message("You will need to choose \x02%d\x0F cards with the 'select X' command, where X is the card's position in your hand." % self.cards_needed, player)
            if self.cards_needed > 1:
                self.message("NOTE: To submit multiple cards, use the cah command 'select X Y ...', where the card numbers are separated by a space.", player)
            # Display hand
            self.message("Ok, here's your hand:", player)
            for num, card in enumerate(player.hand):
                self.message("%d. %s" % (num+1, card.body), player)

    # Choose cards to play
    def select(self, player, cards):
        # Fail if the player is the Czar OR it's not time for players to select cards
        if self.status != "Waiting for player selection" or self.players[self.current_czar].name == player.name:
            self.message("This isn't your turn!", player)
            return

        # Fail if player didn't select the right amount of cards
        if len(cards) != self.cards_needed:
            self.message("You need to play %d cards _only_" % self.cards_needed, player)
            return

        # Fail if cards are invalid (they should have been sanitized to ints in cah.py)
        for card in cards:
            if card > len(player.hand) or card <= 0:
                self.message("You don't have a card %d in your hand!" % card, player)
                return

        # Insert cards into the submissions dictionary
        self.submissions[player] = [player.hand[card-1] for card in cards]
        player.selected_cards = cards

        # Continue on in the game loop if all but the czar have voted
        if len(self.submissions) == len(self.players)-1:
            self.display_selections()
            self.status = "Waiting for Czar vote"

    # Present the funnies
    def display_selections(self):
        self.message("Results are in!")
        # Question cards are only displayed once, then the replies are presented as choices
        if "_" not in self.current_card.body:
            self.message(self.current_card.body)
            for num, submission in enumerate(self.submissions.values()):
                self.message("%d. %s" % (num+1, ', '.join([x.body for x in submission])))
        # Other cards have the white card answeres filled in the blanks (with bold and underline)
        else:
            for num, submission in enumerate(self.submissions.values()):
                replacements = []
                filled_in = self.current_card.body.replace("%","%%").replace("_", "%s")
                for i in range(self.cards_needed):
                    replacements.append("\x02\x1F%s\x0F" % submission[i].body)
                filled_in = filled_in % tuple(replacements)
                self.message("%d. %s" % (num+1, filled_in))

        # Prompt the czar to not be lazy...
        self.message("Now for %s to vote..." % self.players[self.current_czar].name)

    # Czar vote
    def vote(self, player, vote):
        # Fail if the player isn't the current Czar
        if player.name != self.players[self.current_czar].name:
            self.message("You are not the Czar!", player)
            return

        # Fail if it's not time for the Czar to vote
        if self.status != "Waiting for Czar vote":
            self.message("We're not ready for you to vote.", player)
            return

        # Fail if the czar vote for a choice that isn't present
        if vote <= 0 or vote > len(self.players)-1:
            self.message("%d isn't a valid vote selection." % vote, player)
            return

        # Display and increase score for the Czar's choice
        winning_player = self.submissions.keys()[vote-1]
        self.message("%s won this round! The winning combination was..." % winning_player.name)

        winning_player.score += 1

        # TODO: refactor this and the bit in display_selections
        # see display_selections, this is the same, except it only displays a single submission
        if "_" not in self.current_card.body:
            self.message(self.current_card.body)
            self.message(', '.join([x.body for x in self.submissions.values()[vote-1]]))
        else:
            replacements = []
            filled_in = self.current_card.body.replace("%","%%").replace("_", "%s")
            for i in range(self.cards_needed):
                replacements.append("\x02\x1F%s\x0F" % self.submissions.values()[vote-1][i].body)
            filled_in = filled_in % tuple(replacements)
            self.message(filled_in)

        # And start the game loop over
        self.start()

    #deal cards to player until hand size is 10
    def deal(self, player):
        # Sort cards and pop them in reverse order (so the index of the next card to be popped stays the same throughout the loop)
        if player.selected_cards:
            for card in sorted(player.selected_cards, reverse=True):
                player.hand.pop(card-1)
            player.selected_cards = []

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
            self.server.notice(player.name, body)
        else:
            self.server.privmsg(self.channel, body)

    @property
    def cards_needed(self):
        return self.current_card.num_answers

#Utility class to manage Players
class Player(object):
    def __init__(self, name):
        self.name = name  #Player name (IRC nick)
        self.score = 0
        self.hand = []
        self.selected_cards = []
        self.isCzar = False
