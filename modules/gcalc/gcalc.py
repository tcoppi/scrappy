#Google calculator
#Thanks to Actaeus via http://fublag.wordpress.com/2009/04/07/google-calculator-via-python/

import urllib, httplib

from module import Module

class gcalc(Module):
    def __init__(self, bot):
        super(gcalc, self).__init__(bot)

        bot.register_event("gcalc", "msg", self.distribute)

        self.register_cmd("gcalc", self.gcalc)

    def gcalc(self, server, event, bot):
        query = event.tokens[1:]
        query = urllib.urlencode({'q':query})

        if len(query) == 0:
            server.privmsg(event.source, "Error: no query specified.")
            return

        start = '<h2 class=r style="font-size:138%"><b>'
        end = '</b>'
        google = httplib.HTTPConnection("www.google.com")
        google.request("GET","/search?"+query+"&num=1")
        search = google.getresponse()
        data = search.read()

        if data.find(start) == -1:
            server.privmsg(event.target, "Google Calculator results not found.")
        else:
            begin = data.index(start)
            result = data[begin+len(start):begin+data[begin:].index(end)]
            result = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace("\xa0",",")
            server.privmsg(event.source, result)
