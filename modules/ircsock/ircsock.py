# Core IRC socket functions

import irclib_scrappy
import sys

def init(bot):
        bot.ircsock = irclib_scrappy.IRC()
        
        try:
                bot.connection = bot.ircsock.server().connect(bot.server, 
                                bot.port, bot.nickname, username = bot.username, 
                                ircname = bot.realname)
        except irclib_scrappy.ServerConnectionError, x:
                print x
                sys.exit(1)

