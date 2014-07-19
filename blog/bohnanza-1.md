
Hacking Scrappy - Let's start a bean farm!
==========================================
In this series of posts, I'm going to take you through writing a [scrappy](https://github.com/tcoppi/scrappy) module from scratch.

What is scrappy?
----------------
I haven't introduced scrappy yet so let's take a few moments to do that. Scrappy is the project bot of the #hack IRC channel, we've worked on him on and off since ... 2007? The basic overview is that the base bot (scrappy.py) connects to IRC and lets you load modules, which can act on IRC events (usually a PRIVMSG to a channel).
 
Let's brainstorm a module!
--------------------------
A good module would take advantage of the fact that IRC is a multi user terminal. Quickly, what things can you think of that are fun and multi user?
 
Games? 100% correct! The simplest games to implement are those that rely on a user action to advance state. Scrappy is best suited for these types of modules until he gets more support for querying IRC state. We only need to write the module to respond to events, there's no need to have any processing in the background. Boardgames have this attribute (with few exceptions) and the rules are explicitly written, so they would be a good fit.

Now that scrappy's limitations have been considered, we need to work around the limitations of IRC. Remember how I said it was a multi user terminal? It's a pretty poor one. Input needs to be throttled on most servers, there's a lot of noise from everything else happening in a channel, and seemingly everyone has a different client. With that in mind, we need to find a board game that has little or easily compressed state, preferably so that one line will be enough to express the global/individual state. This rules out most games with many varied components (Magic: The Gathering, Dominion). We also want to make sure that we aren't relying on the user's clients to interpret any of the state. For example, assuming everyone is using a monospace font because we want to draw an ASCII board. This rules out most games with boards (Arkham Horror, Agricola). The notable exception is chess, where state changes can be represented with chess notation. However, displaying the complete state of a chess board will take more than one line (correct me if I'm wrong!)

Going through my library alphabetically, Bohnanza is the first game that looks like a good candidate. Now that the game has been chosen, let's code! From here on, I'll assume you're somewhat familiar with the game, but if you're not, then pause for a minute and do some research on [BoardGameGeek](http://boardgamegeek.com/boardgame/11/bohnanza).

<del>Coding Time</del>Planning Time
-----------------------------------
Well... it's not time to code yet. We need to think about how Bohnanza should be mapped to IRC. 

###Game State

I prefer to start planning how the game will be viewed by players and then how players will interact with the game. First, let's talk about game state. In Bohnanza, the player is a bean farmer with 2-3 bean fields that must plant and trade with other players. He will need to refer to:

1. The cards in his hand
2. The contents of the bean fields

The first is private information, so it will need to be sent via NOTICE[1]. One possible way to send it would be in the form `[ID] Card Name (#Cards)`.  You'll notice that cards have an extra piece of information, the number needed to redeem for coins. Instead of putting this information in the hand view, it could be in the field view as current value of field and cards to next coin, but then players would need to be able to see values of cards they don't have in their fields. So, let's try and fit it into the hand view. A format something like this `[ID] Card Name (#Cards X|Y|Z)` (where X,Y,Z are the number of cards to get the respective amount of coins) is dense and will need some explanation, but it would let us compress most hands into a single message. For example, `[3] Blue Bean (20# 4|6|8|10)` shows that the 3rd card is a Blue Bean, there are 20 of them total, and you get coins at 4, 6, 8, and 10 beans harvested.

The second is public information and changes at 3 points: harvest, phase 1 planting, and phase 3 planting, so it will only be necessary to display the player's field at those points in their turn and on demand (probably sent via NOTICE to keep from spamming the channel). Each field will be a single bean type, so the information will compress easily. We'll send fields in the format `PLAYER: Field 1: 7 Blue Beans (2 coins, next at 8 beans), Field 2: 1 Black-Eyed Bean (First coin at 2 beans)`. Even with the maximum three fields, this will easily fit inside one message.
 
###Game Flow

In the last section, we figured out the general output, now it's time to figure out how players interact with the bot to manipulate the state.

Following the same convention from the Cards against Humanity module, we want to start a new game with `!beans new`, which doesn't actually start a game but does allow players to join with `!beans join`. After everyone has joined, `!beans start` will start the game. Note at this point that modules in scrappy are fed all events, so there's not a good way to only enable a module for a specific channel yet. Due to this, all of the game commands for Bohnanza will start with `!beans`[2].
 
 Turns in Bohnanza go clockwise when sitting around a table, but on IRC we'll just cycle through an arbitrary list of the players. If we're feeling creative, we could use the same starting player as the physical game (this is the player to the left of the oldest player), but join order will require less interaction and work just as well.
 
 Each turn consists of 4 phases and one event (harvest) that can happen at any time:
 
 1. Harvest. 
 2. Plant bean cards. 
 3. Draw and trade cards. 
 4. Plant traded cards.
 5. Draw new cards.
 
 Harvest: This can be done at any time by any player. The only argument is the field number. `!beans harvest (1|2|3)` will do for now.
 
 Phase 1: `!beans plant (1|2)` will let the current player plant 1 or 2 beans, but maybe they want to plant one and consider planting another? `!beans plant` should be a shortcut to `!beans plant 1` and both of them should be allowed twice. Before going further, we need to consider the mechanics of planting a bean. In this phase, the top card of your hand is the bean to be planted. With that information already set, it needs a destination field. We'll make the players manually harvest fields and return an error message to the player if they try to plant without an open field. Field order doesn't matter, so if the bean doesn't match, it will go into the first matching or open field. HOWEVER, it's not against the rules to have two or more fields of the same bean (it's just weird, that's all). We should support a completely specified version of the plant command such as `!beans plant (1|2) (1|2|3)` in case a player actually wnats to do that. Thinking of the edge cases we will have to support, we should also consider dropping the ability to plant 2 beans at once. We end up with the command `!beans plant 1 (1|2|3)`. If we're going to be using 1 all the time as the first argument, can't we simplify it to `!beans plant (1|2|3)`? Sure, but now it's kind of ambiguous if the argument is field or beans, because players will start with 2 bean fields. Are there any other instances where we need to plant? Yes, in phase 3. In that phase the player will be able to plant their traded cards in an arbitrary order, so let's give each card a unique identifier. The final command is `!beans plant ID (1|2|3)`. The phase will automatically advance after 2 beans have been planted, but will need to be manually advanced if the player only wants to plant one bean. A simple command would work here, so let's use `!beans trading`.
 
 Phase 2: After the previous phase is over, the bot will draw 2 cards and place them out for trading. In the simplest case, the active player will take those two cards, so a command to end trading is necessary. `!beans end trading`. Let's imagine a few scenarios for trading:
 
 1. Donate cards. "I'll donate 2 stink beans."
 2. Open ended offer. "I'll trade away a blue bean."
 3. Specific offer. "I'll trade you 2 blue beans for a red bean."
 
 Anyone can be on the giving/receiving side of an offer, but all trades must involve the active player. Scenario 2 can be resolved in chat and turned into scenario 3. Scenario 1 can also be collapsed into scenario 3 by allowing offer responses to involve no cards. Putting this into a sequence of events gives:
 
 1. Landon offers one blue bean.
 2. mharrison offers a stink bean for the blue bean.
 3. Landon accepts and the cards are traded.
 
 Changing that to IRC commands, we have :
 
 1. `<Landon> !beans offer 15` (15 is the ID of a specific blue bean that was either drawn or in his hand.)
 2. `<scrappy> New offer: 7. Landon offers a blue bean.`
 3. `<mharrison> !beans respond 7 d4` (d4 is the ID of a specific stink bean in his hand.)
 4. `<scrappy> Landon: Accept trade 1, Blue Bean <-> Stink Bean?`
 5. `<Landon> !beans accept 1`
 
 If the trade was declined, then to keep it simple, we'll just let it sit and clear out the list of trades afte rthis turn instead of having a specific command for declining a trade. The final commands, in order, `!beans offer ID[,ID[,ID[...]]]`, `!beans respond ORDER_ID ID[,ID[,ID[...]]]|-` (- represents an offer of no cards, for a donation), `!beans accept TRADE_ID`. Trade IDs need to be separate form offer IDs so that multiple players can respond to an offer. One good optimization is to keep the active player from considering trades that are no longer valid. This can be accomplished by automatically pruning offers and trades of cards that have already been traded.
 
 With these two lists, we want a way for the player to reference them at any time, so let's use `!beans offers` and `!beans trades`.
 
 Phase 3: Planting traded cards will work similar to Phase 1, players will use the command `!beans plant ID (1|2|3)`, until all of the traded cards have been planted.
 
 Phase 4: No commands necessary, 3 cards will automatically be drawn and the state will advance to Phase 1 for the next player.
 
 With every turn/phase, the current player should be reminded of their options and the command formats.
 
 I think we've got this appropriately planned out by now without touching a line of code. Come back later for part 2, Coder Beans, when we get started writing the basic module.

[1]: With #hack's last game module, Cards Against Humanity, we decided to use notices as much as possible, so that clients can inline messages in the channel. This works slightly better than opening a private message window with the bot, so I'll continue doing it here.

[2]: Elegant improvements to scrappy that would fix this are always welcome!