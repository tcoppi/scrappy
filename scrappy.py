#!/usr/bin/env python
#Let's keep this file in particular as clean and neatly organized as possible.
#If this is nice and organized, then writing new modules will be a snap and this
#file should rarely have to be edited.

import ConfigParser
DEFAULT_CONFIG = "default.conf"
CONFIG_NAME = ".scrappyrc"

import os, os.path
import sys
import traceback
import thread, threading

import irclib_scrappy

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
                # TODO: Use logging module
                debug("Scrappy bot started.")
                #hard-code these for now
                #then write a config loading module

                if not os.path.exists(CONFIG_NAME):
                    print "Error: Configuration file '%s' not found." % CONFIG_NAME
                    print "Copy %s to %s and modify as necessary." % (DEFAULT_CONFIG, CONFIG_NAME)
                    sys.exit(1)
                self.config = ConfigParser.SafeConfigParser()
                self.config.read(CONFIG_NAME)

                self.servers = {}
                required_items = ["cmdchar","nickname","username","realname",
                                    "server","port","channels"]
                for server in self.config.sections():
                    self.servers[server] = {}
                    for (k,v) in self.config.items(server):
                        self.servers[server][k] = v

                    # Sanity check
                    errors = False
                    for item in required_items:
                        if item not in self.servers[server]:
                            errors = True
                            print "Error: %s not found in configuration." % item
                        if errors:
                            sys.exit(1)

                    self.servers[server]["channels"] = self.servers[server]["channels"].split()
                    self.servers[server]["port"] = int(self.servers[server]["port"])

                self.ircsock = '' #this will be the socket
                self.lock = threading.Lock()

                #our event lists.
                #each module adds functions to be called to these events.
                #each event handler calls all of the functions within its list.
                self.events = ["connect", "disconnect", "error", "invite",
                                "join", "kick", "load", "mode", "msg", "part", "ping", "pong",
                                "privmsg", "privnotice", "pubmsg", "pubnotice", "quit"]
                self.modulelist = []
                self.connect_events = []
                self.disconnect_events = []
                self.error_events = []
                self.invite_events = []
                self.join_events = []
                self.kick_events = []
                self.load_events = []
                self.mode_events = []
                self.msg_events = {}
                self.part_events = []
                self.ping_events = []
                self.pong_events = []
                self.privmsg_events = {}
                self.privnotice_events = []
                self.pubmsg_events = {}
                self.pubnotice_events = []
                self.quit_events = [] #for other users quitting, not the bot
                #self.what_other_events? = []

                sys.path.append(os.path.join(os.getcwd(), "modules"))
                #need to load a few modules here - the rest are done elsewhere
                self.load_module("modmanage")
                self.load_module("core")
                #self.load_module("config")

                #self.register_onload_event(loadme)

                #on_load event
                #self.on_load()

                #start the bot
                self.__main()
        ########################################################################
        def parse_argv(self):
                """Parse the commandline args and print a usage message if incorrect."""
                if len(sys.argv) < 3: #Need at least server
                        self.print_usage()
                        sys.exit(1)

                #split out the port if specified
                s = sys.argv[1].split(":", 1)
                self.server = s[0]

                #a port is given
                if len(s) == 2:
                        try:
                                self.port = int(s[1])
                        except ValueError:
                                print "Error: Erroneous port."
                                sys.exit(1)

                self.nickname = sys.argv[2]
                #add channels to chanlist
                for ch in sys.argv[3:]:
                        self.chanlist.append('#%s' % ch)

        def print_usage(self):
                print 'Usage: %s <server[:port]> <nickname> [channel 1 channel 2 ... channelN]' % sys.argv[0]

        ########################################################################
        def __main(self):
                """The real work.  Initialize our connection and register events."""
                #parse comamnd line and create a new socket
                #self.parse_argv()
                self.ircsock = irclib_scrappy.IRC()

                for server in self.servers:
                    server = self.servers[server]
                    try:
                        print server
                        connection = self.ircsock.server().connect(server["server"], server["port"], server["nickname"],
                                                                    username=server["username"], ircname=server["realname"])
                    except irclib_scrappy.ServerConnectionError, err:
                        print err
                        print "Nonfatal Error: %s" % err
                        print "Failed to connect to %s:%s" % (server["server"], server["port"])
                        connection = None

                    server["connection"] = connection

                print self.servers

                #if all goes well, register handlers
                self.connection.add_global_handler("welcome", self.on_connect)
                self.connection.add_global_handler("disconnect", self.on_disconnect)
                self.connection.add_global_handler("error", self.on_error)
                self.connection.add_global_handler("invite", self.on_invite)
                self.connection.add_global_handler("join", self.on_join)
                self.connection.add_global_handler("kick", self.on_kick)
                self.connection.add_global_handler("mode", self.on_mode)
                self.connection.add_global_handler("part", self.on_part)
                self.connection.add_global_handler("ping", self.on_ping)
                self.connection.add_global_handler("pong", self.on_pong)
                self.connection.add_global_handler("privmsg", self.on_privmsg)
                self.connection.add_global_handler("privnotice", self.on_privnotice)
                self.connection.add_global_handler("pubmsg", self.on_privmsg)
                self.connection.add_global_handler("quit", self.on_quit)


                #self.list_modules()

                #enter main event loop after this
                #no code after here
                try:
                        self.ircsock.process_forever()
                except KeyboardInterrupt:
                        self.connection.quit("BAIL OUT!!")


        ########################################################################
        ###################
        #Event Registering#
        ###################

        def register_event(self, modname, event_type, func):
                """Call this with an event_type and a function to call when that event_type happens."""
                #list of legal event types
                #keep in ABC order

                if not event_type in self.events:
                        debug("I don't know what an %s event is." % event_type)
                        return

                #event type is good.  Add it to appropriate event list


                #BUGGY NONWORKING STUFF

                listname = "self."+event_type+"_events"
                #debug(func.__name__)
                #if func.__name__ in eval(listname):
                #	debug("%s already exists in %s! Removing old copy and inserting this..." % (func, listname))
                #	eval(listname).remove(func.__name__)

                eval(listname).setdefault(modname, set()).add(func)
                if event_type == "msg":
                        #self.privmsg_events.append(func)
                        #self.pubmsg_events.append(func)
                        self.privmsg_events.setdefault(modname, set()).add(func)
                        self.pubmsg_events.setdefault(modname, set()).add(func)


        def unregister_event(self, event_type, func):
                pass




        ########################################################################
        ##################
        #Event Handlers  #
        ##################

        def on_connect(self, conn, eventlist):
                """Called when bot makes a connection to the server."""
                #do all of our events
                for func in self.connect_events:
                        thread.start_new_thread(func)

                #if self.identify == True:
                #	conn.privmsg("nickserv", "identify %s"
                #		% self.nickservpass)

                #join channels
                for chan in self.chanlist:
                        if irclib_scrappy.is_channel(chan):
                                conn.join(chan)

        ########################################################################
        def on_disconnect(self, conn, eventlist):
                """Called when the connection to the server is closed."""
                for func in self.disconnect_events:
                        thread.start_new_thread(func)
                conn.quit("Scrappy bot signing off.")
                #do we need to clean stuff up?
                sys.exit(0)

        ########################################################################
        def on_error(self, conn, eventlist):
                debug("Error received: %s" % eventlist.arguments())
                for func in self.error_events:
                        thread.start_new_thread(func)


        ########################################################################
        def on_invite(self, conn, eventlist):
                debug("Received an invite: %s" % eventlist.arguments())
                for func in self.invite_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_join(self, conn, eventlist):
                debug("User joined: %s" % eventlist.arguments())
                for func in self.join_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_kick(self, conn, eventlist):
                debug("Someone was kicked: %s" % eventlist.arguments())
                for func in self.kick_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_mode(self, conn, eventlist):
                debug("Mode change: %s" % eventlist.arguments())
                for func in self.mode_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_part(self, conn, eventlist):
                debug("Part: %s" % eventlist.arguments())
                for func in self.part_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_ping(self, conn, eventlist):
                debug("Ping: %s" % eventlist.arguments())
                for func in self.ping_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_pong(self, conn, eventlist):
                debug("Pong: %s" % eventlist.arguments())
                for func in self.pong_events:
                        thread.start_new_thread(func)

        ########################################################################
        def on_privmsg(self, conn, eventlist):
                """Called when bot receives a private or channel (public) message."""
                #eventlist.arguments() = the message body
                arg = eventlist.arguments()[0]

                iscmd = False #?

                nick = irclib_scrappy.nm_to_n(eventlist.source())
                user = irclib_scrappy.nm_to_u(eventlist.source())
                host = irclib_scrappy.nm_to_h(eventlist.source())


                if arg[0] == self.cmdchar:
                        cmd = arg[1:]
                        iscmd = True
                else:
                        cmd = arg

                params = {'nick' : nick,
                          'user' : user,
                          'host' : host,
                          'iscmd' : iscmd,
                          'cmd' : cmd,
                          'source' : eventlist.target()
                }


                #how can we make the list that's passed to functions more friendly?
                #we end up parsing the list again in the called function...
                #for func in self.privmsg_events:
                #	thread.start_new_thread(func, (conn, [nick, user, host, iscmd, cmd, eventlist.target()], self))
                for funcs in self.privmsg_events.itervalues():
                        for f in funcs:
                                thread.start_new_thread(f, (conn, [nick, user, host, iscmd, cmd, eventlist.target()], self))


        ########################################################################
        def on_privnotice(self, conn, eventlist):
                debug("Privnotice: %s" % eventlist.arguments())
                for func in self.privnotice_events:
                        thread.start_new_thread(func)



        ########################################################################
        #right now this isn't used because it's assumed that privmsg == pubmsg
        #this should probably be changed...
        def on_pubmsg(self, conn, eventlist):
                debug("Pubmsg: % " % eventlist.arguments())
                for func in self.pubmsg_events:
                        func()

        ########################################################################
        def on_quit(self, conn, eventlist):
                debug("Quit: %s" % eventlist.arguments())
                for func in self.quit_events:
                        thread.start_new_thread(func)


        ################
        #Module Loading#
        ################
        def load_module(self, name):
                try:
                        self.modulelist.index(name)
                        #module is already loaded
                        return self.reload_module(name)
                except ValueError:
                        debug("Not Reloading")
                        try:
                                exec("from %s import %s" % (name, name))
                        #module = __import__(name)
                        #debug("Loading %s" % name)
                        except ImportError:
                                #should be error output
                                print "No such module\n"
                                print traceback.print_exc()
                                return "Sorry, there was an error loading %s." % name
                        debug("This should only print once")
                        debug(eval(name).init(self))
                        self.register_module(name,'foo','foo')
                        return "Loaded %s." % name

        def reload_module(self, name):
                debug("Module already loaded, reloading.")
                self.unload_module(name)
                reload(sys.modules[name])
                self.register_module(name, 'foo', 'foo')
                debug(eval(name).init(self))
                return "Reloaded %s." % name

        def unload_module(self, name):
                self.lock.acquire()
                try:
                        self.modulelist.index(name)
                except:
                        print "No such module!"
                        self.lock.release()
                        return "Sorry, no module named %s is loaded." % name
                self.unregister_module(name)
                self.lock.release()
                return "%s unloaded." % name

        def register_module(self, name, eventlist, function):
                self.modulelist.append(name)

        def unregister_module(self, name):
                self.modulelist.remove(name)
                self.msg_events.pop(name)
                self.privmsg_events.pop(name)
                self.pubmsg_events.pop(name)



        def list_modules(self):
                """List currently loaded modules."""
                print "Currently loaded modules:"
                for mod in self.modulelist:
                        print mod


if(__name__ == "__main__"):
        bot = scrappy()

