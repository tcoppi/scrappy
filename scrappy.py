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

from irclib import client as ircclient


# Logging guidelines and levels
# DEBUG - Python debugging (e.g., printing list of connected servers on startup)
# INFO - Anything we would want to see during normal operation (e.g., startup/reboot messages)
# WARNING - Things we would rather not happen (e.g., using a non-SSL connection)
# ERROR - Deviations from normal operation (e.g., failed to connect to a server)
# CRITICAL - Scrappy gonna die! But not before spitting out a final goodbye! (e.g., SIGINT)
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=5)


irc_logger = logging.getLogger("irclib.client")
# Change me if you want to see IRC DEBUG lines
irc_logger.setLevel(logging.INFO)

class scrappy:
    """This is our main bot class. Generally, everything past loading/unloading modules is provided
    by external python modules themselves.
    """
        def __init__(self):
            """Initialize the scrapster
            """

            self.logger = logging.getLogger("scrappy")

            self.logger.info("Scrappy bot started.")

            # Read config file at CONFIG_NAME
            if not os.path.exists(CONFIG_NAME):
                self.logger.critical("Error: Configuration file '%s' not found." % CONFIG_NAME)
                self.logger.critical("Copy %s to %s and modify as necessary." % (DEFAULT_CONFIG, CONFIG_NAME))
                sys.exit(1)
            self.config = ConfigParser.SafeConfigParser()
            self.config.read(CONFIG_NAME)

            self.modules = {}

            #our event lists.
            #each module adds functions to be called to these events.
            #each event handler calls all of the functions within its list.
            # Event types are added as they are registered
            self.events = {"privmsg":{},
                            "pubmsg":{},
                            "tick":{}}

            sys.path.append(os.path.join(os.getcwd(), "modules"))

            # Load these modules before any events occur, since core handles server welcome message
            self.load_module("core")
            self.load_module("modmanage")

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
                        self.logger.warning("Hey, we really don't like you not using SSL!")
                        factory = ircclient.connection.Factory()

                    connection = self.ircsock.server().connect(server["server"], server["port"], server["nickname"],
                                                                username=server["username"], ircname=server["realname"],
                                                                connect_factory=factory)
                except ircclient.ServerConnectionError, err:
                    self.logger.exception("Failed to connect to %s:%s" % (server["server"], server["port"]))
                    connection = None

                #if all goes well, register handlers
                if connection is not None:
                    connection.add_global_handler("all_events", self.process_event)
                    # One second tick for timed functions
                    connection.execute_every(1, self.on_tick, arguments=(connection,))

                server["connection"] = connection

            #enter main event loop after this
            try:
                self.ircsock.process_forever()
            except KeyboardInterrupt:
                for server in self.servers:
                    server = self.servers[server]
                    server["connection"].quit("BAIL OUT!!")

        ########################################################################
        def shutdown(self, code=0):
            """Exit

            Keyword arguments:
            code -- Exit code (default 0)
            """
            sys.exit(code)

        ########################################################################
        def get_server(self, conn):
            """Get the server associated with a connection

            Arguments:
            conn -- connection object
            """
            for server in self.servers:
                server = self.servers[server]
                if conn == server["connection"]:
                    return server

        ########################################################################
        ###################
        #Event Registering#
        ###################

        def register_event(self, modname, event_type, func):
            """Register a callback to an IRC event

            Call this with an event_type and a function to call when that event_type happens.
            Arguments:
            modname -- Modules shortname
            event_type -- Event type, see irclib/events.py for events
            func -- Callback function, needs to have the signature func(server, event, scrappy)
            """

            event_dict = self.events.setdefault(event_type, {})
            event_dict.setdefault(modname, set()).add(func)
            # TODO: Nuke this. Modules can decide if they want both.
            if event_type == "msg":
                self.events["privmsg"].setdefault(modname, set()).add(func)
                self.events["pubmsg"].setdefault(modname, set()).add(func)

        def unregister_event(self, event_type, func):
            """Not Implemented - Unregister a callback to an IRC event
            """
            pass

        ########################################################################
        ##################
        #Event Handlers  #
        ##################

        def process_event(self, conn, event):
            """Processes IRC event on connection

            Arguments:
            conn -- IRC connection
            event -- IRC event
            """
            if event.type in self.events:
                for module_events in self.events[event.type].values():
                    for func in module_events:
                        thread.start_new_thread(func, (self.get_server(conn), event, self))

            # If the on_EVENT method doesn't exist, call a NOP-like function instead
            do_nothing = lambda c, e: None
            custom_handler = getattr(self, "on_" + event.type, do_nothing)
            custom_handler(conn, event)


        ########################################################################
        def on_tick(self, conn):
            """Calls the tick event callbacks

            Arguments:
            conn -- IRC connection
            """
            for module_events in self.events["tick"].values():
                for func in module_events:
                    thread.start_new_thread(func, (self.get_server(conn), self))

        def load_module(self, name):
            """Loads module


            Arguments:
            name -- Name of module
            """
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
            """Reloads module

            Arguments:
            name -- Name of module"""
            self.unload_module(name)
            return self.load_module(name)

        def unload_module(self, name):
            """Unloads module

            May not work consistently, see:
            http://stackoverflow.com/questions/3105801/unload-a-module-in-python

            Arguments:
            name -- Name of module"""
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
            """Unregisters module callbacks

            Arguments:
            name -- Name of module
            """
            for event in self.events.values():
                if name in event:
                    event.pop(name)

if(__name__ == "__main__"):
        bot = scrappy()

