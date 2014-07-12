#CARDS AGAINST HUMANITY!

import threading
from module import Module
from cards import Cards, add_card, init_db

from cards import Deck

from CAHGame import CAHGame

class cah(Module):
        models = [Cards]

        def __init__(self, scrap):
                super(cah, self).__init__(scrap)

                self.lock = threading.Lock()

                self.game = CAHGame()
                        
                scrap.register_event("cah", "msg", self.distribute)
                # but how do you handle commands for privmsg?
                self.register_cmd("cah", self.cah)
                self.register_cmd("cah-init", self.cah_init)

        def cah(self, server, event, bot):
                '''Main command to parse arguments to !cah trigger.'''

                usage = "new, start, join, end, add <black|white> <body>, select <1 2 ... N>,"

                if len(event.tokens) >= 2:
                        arg = event.arg[0]
                        msg = event.arg[1:]

                        if arg == "start":
                                self.cah_start(server, event, bot)
                                
                        elif arg == "new":
                                self.cah_new(server, event, bot)

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
                        elif arg == "draw":
                                color = msg[0]
                                self.cah_draw(server, event, bot, color)
                                
                        elif arg == "madlib":
                                self.cah_madlib(server, event, bot)

                else:
                        server.privmsg(event.target, usage)

################################################################################
# Function prototypes to fill in
################################################################################

        def cah_new(self, server, event, bot):
                '''Initialize a new game.'''
                #check if game is already running
                if self.game.running:
                        msg = "A game is already running!  Use '@cah end' to end it."
                else:
                        msg = "A new game of Cards Against Humanity has started!  Use '%scah join' to join the game." % server.cmdchar
                        self.game = CAHGame()
                        self.game.running = True
                server.privmsg(event.target, msg)
                
        def cah_start(self, server, event, bot):
                '''Start the game once all players have joined..'''
                server.privmsg(event.target, "PLACEHOLDER: starting new game")
                
        def cah_join(self, server, event, bot):
                '''Join the current game.'''
                self.game.add_player(event.source.nick)
                server.privmsg(event.target, "%s joined game." % self.game.players[-1].name)

        def cah_end(self, server, event, bot):
                '''Abort the current game.'''
                #check if game is already running
                if self.game.running:
                        msg = "The game has ended."
                        self.game.running = False
                else:
                        msg = "There's no game running!  Use '@cah new' to start a new game."

                server.privmsg(event.target, msg)

        def cah_add(self, server, event, bot, color, body):
                '''Add a card to the database.'''
                add_card(color, body)
                server.privmsg(event.target, "Added %s card: %s" % (color, body))

        def cah_select(self, server, event, bot, cards):
                '''Select card(s) to play from your hand.'''
                server.privmsg(event.target, "PLACEHOLDER: selecting cards %s" % ', '.join(cards))

        def cah_vote(self, server, event, bot, voted):
                '''Czar voting for group #.'''
                server.privmsg(event.target, "PLACEHOLDER: czar is voting for %s" % voted)

        def cah_init(self, server, event, bot):
            server.privmsg(event.target, "Adding cards to DB")
            init_result = init_db()
            server.privmsg(event.target, init_result)
            
        def cah_draw(self, server, event, bot, color):
                '''For testing only, delete later.'''
                d = Deck()
                c = d.draw(color)
                server.privmsg(event.target, c.body)
                
        def cah_madlib(self, server, event, bot):
                '''Entertaining function for dev, delete later.'''
                d = Deck()
                b = d.draw("black")
                madlib = b.body
                blanks = madlib.count('_')
                if blanks == 0:
                        madlib += ' ' + d.draw("white").body.rstrip('.')
                else:
                        while blanks > 0:
                                w = d.draw("white")
                                madlib = madlib.replace('_', "<<%s>>" % w.body.rstrip('.'), 1)
                                blanks -= 1
                        

                madlib = madlib.replace('<<', '__')
                madlib = madlib.replace('>>', '__')
                server.privmsg(event.target, madlib)
