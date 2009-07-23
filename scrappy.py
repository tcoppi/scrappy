#!/usr/bin/env python2.6
# Thou shalt use a fixed tab size of 8

import irclib_scrappy
import sys
from optparse import OptionParser

DEBUG = True

def debug(msg):
    if DEBUG:
        print msg
class scrappy:
    def __init__(self):
        debug("Scrappy bot started.")
        self.cmdchar = '!'
        self.nickname = 'thetan'
        self.username = 'xenu'
        self.realname = 'xenu'
        self.nickservpass = ''
        self.identify = False
        self.server = ''
        self.port = 6667
        self.chanlist = []
        self.irc = '' #this will be the socket
        self.c = '' #Thomas, explain this to me later

        #testvar, should be gotten rid of
        self.configing = False

        #Experimental stuff for dynamic modules
        #FIXME XXX FIXME XXX
        #probably need to completely redo this mharrison
        self.modulelist = []
        self.privmsg_events = []
        self.pubmsg_events = []
        self.onload_events = []
        self.onquit_events = []
        #self.what_other_events? = []

        #load modules(currently in main())
        sys.path.append("modules/")
        #self.load_module("config")
        #self.load_module("core")

        #start the bot
        self.__main()

    def parse_argv(self):
        """Parse the commandline args and print a usage message if incorrect."""
        parser = OptionParser()
        parser.add_option("--ssl", action="store_true",
                help="Enable SSL support")
        parser.add_option("--server", action="store", type="string",
                help="Server to connect to", metavar="SERVER")
        parser.add_option("--port", action="store", type="int",
                help="Port to connect to. Defaults to 6667 or 6697 for SSL.")
        parser.add_option("--nick", action="store", type="string",
                help="Nickname for the bot")

        (options, args) = parser.parse_args()

        #remaining args are channels
        for ch in args:
            self.chanlist.append('#%s' % ch)

    def __main(self):
        self.parse_argv()
        self.irc = irclib_scrappy.IRC()

        try:
            self.c = self.irc.server().connect(self.server,
                self.port, self.nickname,
                username=self.username, ircname=self.realname)
        except irclib_scrappy.ServerConnectionError, x:
            print x
            sys.exit(1)

        #if all goes well, register handlers
        self.c.add_global_handler("welcome", self.on_connect)
        self.c.add_global_handler("disconnect", self.on_disconnect)
        self.c.add_global_handler("privmsg", self.on_privmsg)
        self.c.add_global_handler("pubmsg", self.on_pubmsg)

        #register some events
        self.register_msg_event(modload_cmd)
        self.register_msg_event(modlist_cmd)

        self.list_modules()

        #nothng after this executes
        self.irc.process_forever()

    ##################
    #Event Processing#
    ##################
    def register_privmsg_event(self, func):
            self.privmsg_events.append(func)

    def register_pubmsg_event(self, func):
            self.pubmsg_events.append(func)

    #Convenience function, registers the func
    #for both privmsgs and pubmsgs
    def register_msg_event(self, func):
            self.register_privmsg_event(func)
            self.register_pubmsg_event(func)

    def register_onload_event(self, func):
            self.onload_events.append(func)

    def register_onquit_event(self, func):
            self.onquit_events.append(func)

    ################
    #Event Handlers#
    ################
    def on_connect(self, c, event):
            for ch in self.chanlist:
                    if irclib_scrappy.is_channel(ch):
                            c.join(ch)

            if self.identify == True:
                self.c.privmsg("nickserv", "identify %s" % self.nickservpass)

    #FIXME XXX
    #XXX FIXME
    #This needs to be completely redone in a clean way, not just passing
    #lists of crap to our handlers
    def on_pubmsg(self, c, event):
            arg = event.arguments()[0]
            iscmd = False

            nick = irclib_scrappy.nm_to_n(event.source())
            user = irclib_scrappy.nm_to_u(event.source())
            host = irclib_scrappy.nm_to_h(event.source())

            debug(nick)

            if arg[0] == self.cmdchar:
                    cmd = arg[1:]
                    iscmd = True
            else:
                    cmd = arg

            #dispatch the command
            for func in self.pubmsg_events:
                    func(c, [nick, user, host, iscmd, cmd, event.target()], self)

    def on_privmsg(self, c, event):
            cmd = event.arguments()[0]
            iscmd = False

            nick = irclib_scrappy.nm_to_n(event.source())
            user = irclib_scrappy.nm_to_u(event.source())
            host = irclib_scrappy.nm_to_h(event.source())

            if cmd[0] == self.cmdchar:
                    c.privmsg(nick, "You privmsged me, you don't need to " +
                    "prefix commands with %s" % self.cmdchar)
                    cmd = cmd[1:]

            iscmd = True

            #dispatch the command
            for func in self.privmsg_events:
                    func(c, [nick, user, host, iscmd, cmd, event.target()], self)


    def on_disconnect(self, c, event):
            for func in self.onquit_events:
                    func()

            sys.exit(0)

    def on_load(self):
            for func in self.onload_events:
                    func(self)

    ################
    #Module Loading#
    ################
    #FIXME This needs to be redone as well
    def load_module(self, name):
            #maybe we should keep the module around?
            try:
                    module = __import__("%s" % name)
            except ImportError:
                    #should be error output
                    print "No such module\n"
                    return

            module.__init__(self)
            self.register_module(name, 'foo', 'foo')

    def register_module(self, name, eventlist, function):
            self.modulelist.append(name)

    def list_modules(self):
            """List currently loaded modules."""
            print "Currently loaded modules:"
            for mod in self.modulelist:
                    print mod


if(__name__ == "__main__"):
    bot = scrappy()

