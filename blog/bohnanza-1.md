
Hacking Scrappy - Let's start a bean farm!
==========================================
In this series of posts, I'm going to take you through writing a [scrappy](https://github.com/tcoppi/scrappy) module from scratch

What is scrappy?
----------------
Since I haven't introduced scrappy yet, let's take a few moments to do that. Scrappy is the project bot of the #hack IRC channel, we've worked on him on and off since ... 2007? The basic overview is that the base bot (scrappy.py) connects to IRC and lets you load modules, which can act on IRC events (usually a PRIVMSG to a channel).
 
Let's brainstorm a module!
--------------------------
A good module would take advantage of the fact that IRC is a multi user terminal. Quickly, what things can you think of that are fun and multi user?
 
Games? 100% correct! The simplest games to implement are those that rely on a user action to advance state. In scrappy's current state, this means we only need to write the module to respond to events, there's no need to have any processing in the background. Boardgames have this attribute (with few exceptions) and the rules are explicitly written, so they would be a good fit.

Now that scrappy's limitations have been considered, we need to work around the limitations of IRC. Remember how I said it was a multi user terminal? It's a pretty poor one. Input needs to be throttled on most servers, there's a lot of noise from everything else happening in a channel, and seemingly everyone has a different client. With that in mind, we need to find a board game that has little or easily compressed state, preferably so that one line will be enough to express the global/individual state. This rules out most games with many varied components (Magic: The Gathering, Dominion). We also want to make sure that we aren't relying on the user's clients to interpret any of the state. For example, assuming everyone is using a monospace font because we want to draw an ASCII board. This rules out most games with boards (Arkham Horror, Agricola). The notable exception is chess, where state changes can be represented with chess notation. However, displaying the complete state of a chess board will take more than one line (correct me if I'm wrong!)

Going through my library alphabetically, Bohnanza is the first game that looks like a good candidate. Now that the game has been chosen, let's code! From here on, I'll assume you're somewhat familiar with the game, but if you're not, then go look it up on [BoardGameGeek](http://boardgamegeek.com/boardgame/11/bohnanza).

<del>Coding Time</del>Planning Time
-----------------------------------
Well... it's not time to code yet. We need to think about how Bohnanza should be mapped to IRC. 

###Game State

I prefer to start planning how the game will be viewed by players and then First, let's talk about game state. In Bohnanza, the player is a bean farmer with 2-3 bean fields that must plant and trade with other players. He will need to refer to:

1. The cards in his hand
2. The contents of the bean fields

The first is private information, so it will need to be sent via NOTICE[1]. One possible way to send it would be in the form `[ID] Card Name (#Cards)`  You'll notice that cards have an extra piece of information, the number needed to redeem for coins. Instead of putting this information in the hand view, it could be in the field view as current value of field and cards to next coin, but then players would need to be able to see values of cards they don't have in their fields. So, let's try and fit it into the hand view. A format something like this `[ID] Card Name (#Cards X|Y|Z)` (where X,Y,Z are the number of cards to get the respective amount of coins) is dense and will need some explanation, but it would let us compress most hands into a single message. For example, `[3] Blue Bean (20# 4|6|8|10)` shows that the 3rd card is a Blue Bean, there are 20 of them total, and you get coins at 4, 6, 8, and 10 beans harvested.

The second is public information and changes at 3 points: harvest, phase 1 planting, and phase 3 planting, so it will only be necessary to display the player's field at those points in their turn and on demand (probably sent via NOTICE to keep from spamming the channel). Each field will be a single bean type, so the information will compress easily. We'll send fields in the format `PLAYER: Field 1: 7 Blue Beans (2 coins, next at 8 beans), Field 2: 1 Black-Eyed Bean (First coin at 2 beans)`. Even with the maximum three fields, this will easily fit inside one message.

###Game Flow

In the last section, we figured out the general output, now it's time to figure out how players interact with the bot to manipulate the state.
CONTINUE FROM HERE

[1]: With #hack's last game module, Cards Against Humanity, we decided to use notices as much as possible, so that clients can inline messages in the channel. This works slightly better than opening a private message window with the bot, so I'll continue doing it here.