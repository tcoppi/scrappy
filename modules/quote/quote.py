import json
import urllib2

from module import Module

#TODO: This could get pretty spammy, need to be able to allow it per channel
class quote(Module):
    def __init__(self, scrap):
        super(quote, self).__init__(scrap)
        scrap.register_event("quote", "join", self.give_quote)

    def give_quote(self, server, event, bot):
        nick = event.source.nick

        quote_json = urllib2.urlopen("http://www.iheartquotes.com/api/v1/random?max_lines=1&format=json").read()
        quote_info = json.loads(quote_json)
        quote = quote_info["quote"]

        server.privmsg(event.target, "%s: %s" % (nick, quote))



