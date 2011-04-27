#!/usr/bin/env python
#Let's keep this file in particular as clean and neatly organized as possible.
#If this is nice and organized, then writing new modules will be a snap and this
#file should rarely have to be edited.

#import irclib_scrappy
import sys, os
import traceback
import thread, threading

################################################################################
#set to False to turn off debugging to stdout
DEBUG = True

def debug(msg):
        if DEBUG:
                print msg

################################################################################


#this is our main bot class.  Once scrappy.py is called, an instance of this
#class (our bot) gets created and some initialization is done.  The real work is
#done via modules that get loaded here.

class scrappy:
                
        def __init__(self):
                debug("Scrappy bot started.")
                self.ircsock = ""
                self.connection = ""
                self.modulelist = []
                self.lock = threading.Lock()

                #module loading/bootstrap
                sys.path.append(os.path.join(os.getcwd(), "modules"))
                #Don't change the order of these
                self.load_module("config")
                self.load_module("ircsock")
                self.load_module("eventhandler")
                for m in self.startup:
                        self.load_module(m)
                
                #start the bot
                self.__main()

                
        ########################################################################
        def __main(self):
                """The real work.  Initialize our connection and register events."""
                #parse comamnd line and create a new socket
                #self.parse_argv()

                try:
                        self.ircsock.process_forever()
                except KeyboardInterrupt:
                        self.connection.quit("BAIL OUT!")
                        
                        
        ########################################################################
        ###################
        #Event Registering#
        ###################

        def register_event(self, modname, event_type, func):
                """Call this with an event_type and a function to call when that event_type happens."""

                if not event_type in self.events:
                        debug("I don't know what an %s event is." % event_type)
                        return

                listname = "self."+event_type+"_events"

                eval(listname).setdefault(modname, set()).add(func)
                if event_type == "msg":
                        self.privmsg_events.setdefault(modname, set()).add(func)
                        self.pubmsg_events.setdefault(modname, set()).add(func)


        def unregister_event(self, event_type, func):
                pass
                
        ################
        #Module Loading#
        ################
        def load_module(self,name):
                try:
                        self.modulelist.index(name)
                        #module is already loaded
                        return #self.reload_module(name)
                except ValueError:
                        debug("Not Reloading")
                        try:
                                exec("from %s import %s" % (name, name))

                        except ImportError:
                                debug(traceback.print_exc())
                                return "Sorry, there was an error loading %s." % name
                        debug(eval(name).init(self))
                        #self.register_module(name,'foo','foo')
                        return "Loaded %s." % name
        
                        
if(__name__ == "__main__"):
        bot = scrappy()
