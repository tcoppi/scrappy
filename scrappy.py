#!/usr/bin/env python
#Let's keep this file in particular as clean and neatly organized as possible.
#If this is nice and organized, then writing new modules will be a snap and this
#file should rarely have to be edited.

import ConfigParser
DEFAULT_CONFIG = "default.conf"
CONFIG_NAME = ".scrappyrc"

import logging
import os, os.path
import ssl
import sys
import traceback
import thread, threading

#import irclib_scrappy
#import irclib
from irclib import client as ircclient


# Logging guidelines and levels
# DEBUG - Python debugging (e.g., printing list of connected servers on startup)
# INFO - Anything we would want to see during normal operation (e.g., startup/reboot messages)
# WARNING - Things we would rather not happen (e.g., using a non-SSL connection)
# ERROR - Deviations from normal operation (e.g., failed to connect to a server)
# CRITICAL - Scrappy gonna die! But not before spitting out a final goodbye! (e.g., SIGINT)
logging.basicConfig(level=logging.DEBUG)


irc_logger = logging.getLogger("irclib.client")
# Change me if you want to see IRC DEBUG lines
irc_logger.setLevel(logging.INFO)

#this is our main bot class.  Once scrappy.py is called, an instance of this
#class (our bot) gets created and some initialization is done.  The real work is
#done via modules that get loaded here.
class scrappy:
        def __init__(self):

            self.logger = logging.getLogger("scrappy")

            # TODO: Use logging module
            self.logger.info("Scrappy bot started.")

            if not os.path.exists(CONFIG_NAME):
                self.logger.critical("Error: Configuration file '%s' not found." % CONFIG_NAME)
                self.logger.critical("Copy %s to %s and modify as necessary." % (DEFAULT_CONFIG, CONFIG_NAME))
                sys.exit(1)
            self.config = ConfigParser.SafeConfigParser()
            self.config.read(CONFIG_NAME)

            self.servers = {}
            required_items = ["cmdchar","nickname","username","realname",
                                "server","port","channels", "ssl"]
            for server in self.config.sections():
                self.servers[server] = {}
                for (k,v) in self.config.items(server):
                    self.servers[server][k] = v

                # Ok ok, so ssl is already a key, but I want to coerce it to bool
                self.servers[server]["ssl"] = self.config.getboolean(server, "ssl")

                # Sanity check
                errors = False
                for item in required_items:
                    if item not in self.servers[server]:
                        errors = True
                        self.logger.critical("Error: %s not found in configuration." % item)
                    if errors:
                        sys.exit(1)

                self.servers[server]["channels"] = self.servers[server]["channels"].split()
                self.servers[server]["port"] = int(self.servers[server]["port"])

            self.ircsock = '' #this will be the socket
            self.lock = threading.Lock()

            #our event lists.
            #each module adds functions to be called to these events.
            #each event handler calls all of the functions within its list.
            self.events = {"connect": {},
                            "disconnect": {},
                            "error": {},
                            "invite": {},
                            "join": {},
                            "kick": {},
                            "load": {},
                            "mode": {},
                            "msg": {},
                            "part": {},
                            "ping": {},
                            "pong": {},
                            "privmsg": {},
                            "privnotice": {},
                            "pubmsg": {},
                            "privmsg": {},
                            "pubnotice": {},
                            "quit": {},
                            "tick": {}}

            self.modules = {}
            #TODO: Necessary with using __import__?
            sys.path.append(os.path.join(os.getcwd(), "modules"))

            #need to load a few modules here - the rest are done elsewhere
            self.load_module("modmanage")
            self.load_module("core")

            #start the bot
            self.__main()

        ########################################################################
        def __main(self):
            """The real work.  Initialize our connection and register events."""
            # Save arguments for rebooting (see 'core' module)
            self.argv = sys.argv
            # Create a new socket
            self.ircsock = ircclient.IRC()

            for server in self.servers:
                server = self.servers[server]
                try:
                    if server["ssl"]:
                        factory = ircclient.connection.Factory(wrapper=ssl.wrap_socket)
                    else:
                        self.logger.warning("Hey, we really don't like you not using SSL")
                        factory = ircclient.connection.Factory()

                    connection = self.ircsock.server().connect(server["server"], server["port"], server["nickname"],
                                                                username=server["username"], ircname=server["realname"],
                                                                connect_factory=factory)
                except ircclient.ServerConnectionError, err:
                    self.logger.exception("Failed to connect to %s:%s" % (server["server"], server["port"]))
                    connection = None

                #if all goes well, register handlers
                #TODO: What ones are we missing?
                if connection is not None:
                    connection.add_global_handler("welcome", self.on_connect)
                    connection.add_global_handler("disconnect", self.on_disconnect)
                    connection.add_global_handler("error", self.on_error)
                    connection.add_global_handler("invite", self.on_invite)
                    connection.add_global_handler("join", self.on_join)
                    connection.add_global_handler("kick", self.on_kick)
                    connection.add_global_handler("mode", self.on_mode)
                    connection.add_global_handler("part", self.on_part)
                    connection.add_global_handler("ping", self.on_ping)
                    connection.add_global_handler("pong", self.on_pong)
                    connection.add_global_handler("privmsg", self.on_privmsg)
                    connection.add_global_handler("privnotice", self.on_privnotice)
                    connection.add_global_handler("pubmsg", self.on_privmsg)
                    connection.add_global_handler("quit", self.on_quit)
                    connection.execute_every(5, self.on_tick, arguments=(connection,))

                server["connection"] = connection

            #enter main event loop after this
            #no code after here
            try:
                self.ircsock.process_forever()
            except KeyboardInterrupt:
                for server in self.servers:
                    server = self.servers[server]
                    server["connection"].quit("BAIL OUT!!")

        ########################################################################
        def get_server(self, conn):
            for server in self.servers:
                server = self.servers[server]
                if conn == server["connection"]:
                    return server

        ########################################################################
        ###################
        #Event Registering#
        ###################

        def register_event(self, modname, event_type, func):
            """Call this with an event_type and a function to call when that event_type happens."""

            if not event_type in self.events:
                self.logger.error("I don't know what an %s event is." % event_type)
                return

            event_dict = self.events[event_type]
            event_dict.setdefault(modname, set()).add(func)
            #TODO: Catchall msg event as well as separate privmsg and pubmsg events?
            if event_type == "msg":
                self.events["privmsg"].setdefault(modname, set()).add(func)
                self.events["pubmsg"].setdefault(modname, set()).add(func)

        def unregister_event(self, event_type, func):
                pass

        ########################################################################
        ##################
        #Event Handlers  #
        ##################
        def process_events(self, event_name, conn, event):
            #TODO: Custom events for classes that need it, like privmsg
            for module_events in self.events[event_name].values():
                for func in module_events:
                    thread.start_new_thread(func, (self.get_server(conn), event, self))

        ########################################################################
        def on_tick(self, conn):
            for module_events in self.events["tick"].values():
                for func in module_events:
                    thread.start_new_thread(func, (self.get_server(conn), self))


        ########################################################################
        def on_connect(self, conn, event):
            """Called when bot makes a connection to the server."""
            self.process_events("connect", conn, event)

            #if self.identify == True:
            #	conn.privmsg("nickserv", "identify %s"
            #		% self.nickservpass)

            #join channels
            server = self.get_server(conn)
            for chan in server["channels"]:
                if ircclient.is_channel(chan):
                    conn.join(chan)

        ########################################################################
        def on_disconnect(self, conn, event):
            """Called when the connection to the server is closed."""
            self.process_events("disconnect", conn, event)
            conn.quit("Scrappy bot signing off.")

            #do we need to clean stuff up?
            # TODO: Check if this is the last active connection, then quit
            # TODO: Maybe set server["connection"] = None if the conn object has no connected() method
            sys.exit(0)

        ########################################################################
        def on_error(self, conn, event):
            self.process_events("error", conn, event)

        ########################################################################
        def on_invite(self, conn, event):
            self.process_events("invite", conn, event)

        ########################################################################
        def on_join(self, conn, event):
            self.process_events("join", conn, event)

        ########################################################################
        def on_kick(self, conn, event):
            self.process_events("kick", conn, event)

        ########################################################################
        def on_mode(self, conn, event):
            self.process_events("mode", conn, event)

        ########################################################################
        def on_part(self, conn, event):
            self.process_events("part", conn, event)

        ########################################################################
        def on_ping(self, conn, event):
            self.process_events("ping", conn, event)

        ########################################################################
        def on_pong(self, conn, event):
            self.process_events("pong", conn, event)

        ########################################################################
        def on_privmsg(self, conn, event):
            """Called when bot receives a private or channel (public) message."""
            #eventlist.arguments() = the message body
            server = self.get_server(conn)
            event.arg = event.arguments[0]

            event.iscmd = False #?

            event.nick = event.source.nick
            event.user = event.source.user
            event.host = event.source.host

            if event.arg[0] == server["cmdchar"]:
                event.cmd = event.arg[1:]
                event.iscmd = True
            else:
                event.cmd = event.arg

            #event.source = event.target() # TODO: Explain this to me

            self.process_events("privmsg", conn, event)

            #params = {'nick' : nick,
            #          'user' : user,
            #          'host' : host,
            #          'iscmd' : iscmd,
            #          'cmd' : cmd,
            #          'source' : event.target() # What
            #}


            #how can we make the list that's passed to functions more friendly?
            #we end up parsing the list again in the called function...
            #for func in self.privmsg_events:
            #	thread.start_new_thread(func, (conn, [nick, user, host, iscmd, cmd, event.target()], self))
            #for funcs in self.privmsg_events.itervalues():
            #    for f in funcs:
            #        thread.start_new_thread(f, (server, [nick, user, host, iscmd, cmd, event.target()], self))


        ########################################################################
        def on_privnotice(self, conn, event):
            self.process_events("privnotice", conn, event)

        ########################################################################
        #right now this isn't used because it's assumed that privmsg == pubmsg
        #this should probably be changed...
        def on_pubmsg(self, conn, event):
            self.process_events("pubmsg", conn, event)

        ########################################################################
        def on_quit(self, conn, event):
            self.process_events("quit", conn, event)

        ################
        #Module Loading#
        ################
        #TODO: Return booleans, maybe raise exceptions if necessary
        def load_module(self, name):
            self.logger.debug("Loading module %s." % name)
            if name in self.modules:
                self.logger.debug("Actually, module %s already loaded, reloading.")
                return self.reload_module(name)

            try:
                package = __import__(name+"."+name)
                module = getattr(package, name)
                cls = getattr(module, name)
            except AttributeError:
                self.logger.exception("Error: module %s.%s not found, make sure %s/%s.py exists" % (name,name,name,name))
                return "Sorry, there was an error loading %s." % name
            except ImportError:
                self.logger.exception("No such module %s" % name)
                return "Sorry, there was an error loading %s." % name

            try:
                self.modules[name] = cls(self)
            except Exception as err:
                self.logger.exception("Error: Module failed to initialize")
                return "Sorry, there was an error loading %s." % name

            return "Loaded %s." % name

        def reload_module(self, name):
            self.unload_module(name)
            return self.load_module(name)

        def unload_module(self, name):
            with self.lock:
                if name in self.modules:
                    self.unregister_module(name)
                    self.modules.pop(name)
                    fullname = name+"."+name
                    if fullname in sys.modules:
                        # Package name is kept in sys.modules, but it doesn't seem to care if I don't delete it
                        #del(sys.modules[name])
                        del(sys.modules[fullname])
                else:
                    #self.lock.release()
                    return "Sorry, no module named %s is loaded." % name

            return "%s unloaded." % name

        def unregister_module(self, name):
            for event in self.events.values():
                if name in event:
                    event.pop(name)

if(__name__ == "__main__"):
        bot = scrappy()

