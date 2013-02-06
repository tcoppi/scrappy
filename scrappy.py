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
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=5)


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
                self.servers[server]["servername"] = server

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
                    connection.add_global_handler("all_events", self.process_event)
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
        def shutdown(self, code=0):
            sys.exit(code)

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

            event_dict = self.events.setdefault(event_type, {})
            event_dict.setdefault(modname, set()).add(func)
            #TODO: Catchall msg event as well as separate privmsg and pubmsg events?
            # TODO: Nuke this. Modules can decide if they want both.
            if event_type == "msg":
                self.events["privmsg"].setdefault(modname, set()).add(func)
                self.events["pubmsg"].setdefault(modname, set()).add(func)

        def unregister_event(self, event_type, func):
                pass

        ########################################################################
        ##################
        #Event Handlers  #
        ##################

        def process_event(self, conn, event):
            #self.logger.log(5, "%s: %s" % (event.type, event.arguments))
            # Preserve privmsg/pubmsg interface for now:
            if event.type in ["privmsg", "pubmsg"]:
                return self.on_privmsg(conn, event)

            if event.type in self.events:
                for module_events in self.events[event.type].values():
                    for func in module_events:
                        thread.start_new_thread(func, (self.get_server(conn), event, self))

            do_nothing = lambda c, e: None
            custom_handler = getattr(self, "on_" + event.type, do_nothing)
            custom_handler(conn, event)


        ########################################################################
        def on_tick(self, conn):
            for module_events in self.events["tick"].values():
                for func in module_events:
                    thread.start_new_thread(func, (self.get_server(conn), self))

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

            event.cmdchar = server["cmdchar"]
            #event.source = event.target() # TODO: Explain this to me

            for module_events in self.events[event.type].values():
                for func in module_events:
                        thread.start_new_thread(func, (self.get_server(conn), event, self))

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

        ################
        #Module Loading#
        ################
        def load_module(self, name):
            self.logger.debug("Loading module '%s'." % name)
            if name in self.modules:
                self.logger.debug("Actually, module '%s' already loaded, reloading." % name)
                return self.reload_module(name)

            try:
                package = __import__(name+"."+name)
                module = getattr(package, name)
                cls = getattr(module, name)
            except AttributeError as err:
                self.logger.exception("Module '%s' not found, make sure %s/%s.py exists." % (name,name,name,name))
                raise err
            except ImportError as err:
                self.logger.exception("No such module '%s'." % name)
                raise err
            except Exception as err:
                self.logger.exception("Error loading module '%s': %s" % (name, err))
                raise err

            try:
                self.modules[name] = cls(self)
            except Exception as err:
                self.logger.exception("Module '%s' failed to initialize." % name)
                raise err

            return True

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
                    return False

            return True

        def unregister_module(self, name):
            for event in self.events.values():
                if name in event:
                    event.pop(name)

if(__name__ == "__main__"):
        bot = scrappy()

