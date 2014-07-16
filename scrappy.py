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
import time

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
#irc_logger.setLevel(logging.DEBUG)

# State classes

class User(object):
    def __init__(self, server, nick, host=None):
        self.server = server
        self.nick = nick
        self._host = host

        self.channels = {}

    @property
    def host(self):
        if self._host is None:
            self.server.whois((self.nick,))
            timeout = 1
            time_spent = 0
            while self._host is None and timeout > 0:
                timeout -= .01
                time.sleep(.01)
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    def join(self, channel):
        channel.usercount += 1
        self.channels[channel.name] = channel

    def part(self, channel):
        channel.usercount -= 1
        self.channels.remove(channel)

    def quit(self):
        for channel in self.channels:
            self.channels[channel].usercount -= 1

    def __str__(self):
        return "%s@%s" % (self.nick, self._host)

    def __repr__(self):
        return self.__str__()

#TODO: use weakref dictionaries for the users
class Channel(object):
    def __init__(self, server, channel_name):
        self.logger = server.logger.getChild(channel_name)
        self.server = server
        self.name = channel_name.lower()
        self.usercount = 0

class ServerState(ircclient.ServerConnection):
    def __init__(self, name, config, bot, irclibobj):
        super(ServerState, self).__init__(irclibobj)
        irclibobj.add_connection(self)

        self.logger = bot.logger.getChild(name)
        self.server_name = name

        # Register handlers
        self.add_global_handler("all_events", bot.process_event)
        # One second tick for timed functions
        self.execute_every(1, bot.on_tick, arguments=(self,))

        bot.register_event("server-%s"%name,"welcome", self.join_defaults)
        bot.register_event("server-%s"%name,"join", self.update_channel)
        bot.register_event("server-%s"%name,"part", self.update_channel)
        bot.register_event("server-%s"%name,"kick", self.update_channel)
        bot.register_event("server-%s"%name,"quit", self.update_channel)
        bot.register_event("server-%s"%name,"namreply", self.on_namereply)
        bot.register_event("server-%s"%name,"whoisuser", self.on_whoisreply)

        if "password" in config:
            password = config["password"]
        else:
            password = None

        if config["ssl"].lower() == "yes":
            factory = ircclient.connection.Factory(wrapper=ssl.wrap_socket)
        else:
            self.logger.warning("Hey, we really don't like you not using SSL!")
            factory = ircclient.connection.Factory()

        try:
            self.connect(config["server"], int(config["port"]), config["nickname"], password=password,
                        username=config["username"], ircname=config["realname"], connect_factory=factory)
        except ircclient.ServerConnectionError, err:
            self.logger.exception("Failed to connect on port %s" % (config["port"]))

        self.cmdchar = config["cmdchar"]
        self.config = config

        self.channels = {}
        self.initial_channels = config["channels"].split()

        self.users = {}

        self.temp_state = {}

        #self.channels = [Channel(x) for x in config["channels"].split()]

    # Reply to a PRIVMSG event
    def reply(self, event, message):
        if event.type == "privmsg":
            self.privmsg(event.source.nick, message)
        elif event.type == "pubmsg":
            self.privmsg(event.target, message)

    def join_defaults(self, server, event, bot):
        if server == self:
            for channel in self.initial_channels:
                self.join(channel)

    def update_channel(self, server, event, bot):
        if server == self:
            if event.type == "kick":
                nick = event.arguments[0]
                host = None
            elif event.type =="part" or event.type == "join" or event.type == "quit":
                nick = event.source.nick
                host = event.source.host

            if nick not in self.users:
                self.users[nick] = User(self, nick, host)
            user = self.users[nick]

            if event.type == "quit":
                user.quit()
                for channel in user.channels:
                    if self.channels[channel].usercount == 0:
                        del self.channels[channel]
                del self.users[nick]
                return

            if event.target not in self.channels:
                self.channels[event.target] = Channel(self, event.target)
            channel = Channel(self, event.target)

            if event.type == "join":
                user.join(channel)
            elif event.type == "part" or event.type == "kick":
                # TODO: Need to take care of the part when _I_ part a channel, shouldn't track its state anymore
                user.part(channel)
                if len(user.channels) == 0:
                    del self.users[user.nick]
                if channel.usercount == 0:
                    del self.channels[channel.name]

    def on_namereply(self, server, event, bot):
        if server == self:
            # Hoping that the namreply is only additive! In theory, we shouldn't have missed any users leaving channels though
            if event.type == "namreply":
                channel_name = event.arguments[1]
                if channel_name not in self.channels:
                    self.channels[channel_name] = Channel(self, channel_name)
                channel = self.channels[channel_name]

                nicks = event.arguments[2].strip()
                for nick in nicks.split(" "):
                    if nick not in self.users:
                        self.users[nick] = User(self, nick)
                    self.users[nick].join(channel)

    def on_whoisreply(self, server, event, bot):
        if server == self:
            if event.type == "whoisuser":
                nick = event.arguments[0]
                host = event.arguments[2]
                try:
                    user = self.users[nick]
                    user.host = host
                except KeyError:
                    return # ignore the reply, we don't know about this user

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

        # Load these modules before any events occur, since core handles server welcome message
        self.load_module("core")
        self.load_module("modmanage")

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

        self.servers = {}
        for servername in self.config.sections():
            server = ServerState(servername, dict(self.config.items(servername)), self, self.ircsock)
            self.servers[servername] = server

        #enter main event loop after this
        try:
            self.ircsock.process_forever()
        except KeyboardInterrupt:
            for server in self.servers:
                self.servers[server].quit("BAIL OUT!!")

    ########################################################################
    def shutdown(self, code=0):
        """Exit

        Keyword arguments:
        code -- Exit code (default 0)
        """
        sys.exit(code)

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
                    thread.start_new_thread(func, (conn, event, self))

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
                thread.start_new_thread(func, (conn, self))

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
            # from modules.core.core import core
            module = __import__("modules.%s.%s" % (name, name), globals(), locals(), [name])
            # Get the class
            cls = getattr(module, name)
        except AttributeError as err:
            self.logger.exception("Module '%s' not found, make sure %s/%s.py exists." % (name,name,name))
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

