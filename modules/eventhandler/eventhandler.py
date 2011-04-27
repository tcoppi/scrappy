# Event handlers
import thread, threading

def init(bot):
        #our event lists.
        #each module adds functions to be called to these events.
        #each event handler calls all of the functions within its list.
        bot.events = ["connect", "disconnect", "error", "invite",
        "join", "kick", "load", "mode", "msg", "part", "ping", "pong",
        "privmsg", "privnotice", "pubmsg", "pubnotice", "quit"]
                
        
        bot.connect_events = []
        bot.disconnect_events = []
        bot.error_events = []
        bot.invite_events = []
        bot.join_events = []
        bot.kick_events = []
        bot.load_events = []
        bot.mode_events = []
        bot.msg_events = {}
        bot.part_events = []
        bot.ping_events = []
        bot.pong_events = []
        bot.privmsg_events = {}
        bot.privnotice_events = []
        bot.pubmsg_events = {}
        bot.pubnotice_events = []
        bot.quit_events = [] #for other users quitting, not the bot
        #bot.what_other_events? = []
        
        add_handlers(bot)

class eventhandler:
        def __init__(self, bot):
                self.bot = bot
        
        def on_connect(self, conn, eventlist):
                """Called when bot makes a connection to the server."""
                #do all of our events
                for func in self.bot.connect_events:
                        thread.start_new_thread(func)

                for chan in self.bot.chanlist:
                        conn.join(chan) 

def add_handlers(bot):
        bot.eventhandler = eventhandler(bot)
        bot.connection.add_global_handler("welcome", bot.eventhandler.on_connect)
        #bot.connection.add_global_handler("disconnect", bot.eventhandler.on_disconnect)
        #bot.connection.add_global_handler("error", bot.eventhandler.on_error)
        #bot.connection.add_global_handler("invite", bot.eventhandler.on_invite)
        #bot.connection.add_global_handler("join", bot.eventhandler.on_join)
        #bot.connection.add_global_handler("kick", bot.eventhandler.on_kick)
        #bot.connection.add_global_handler("mode", bot.eventhandler.on_mode)
        #bot.connection.add_global_handler("part", bot.eventhandler.on_part)
        #bot.connection.add_global_handler("ping", bot.eventhandler.on_ping)
        #bot.connection.add_global_handler("pong", bot.eventhandler.on_pong)
        #bot.connection.add_global_handler("privmsg", bot.eventhandler.on_privmsg)
        #bot.connection.add_global_handler("privnotice", bot.eventhandler.on_privnotice)
        #bot.connection.add_global_handler("pubmsg", bot.eventhandler.on_privmsg)
        #bot.connection.add_global_handler("quit", bot.eventhandler.on_quit)
