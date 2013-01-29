#Google calculator
#Thanks to Actaeus via http://fublag.wordpress.com/2009/04/07/google-calculator-via-python/

import urllib, httplib

def init(bot):
	bot.register_event("gcalc", "msg", gcalc)

def gcalc(server, args, bot):
    c = server["connection"]
    cmd = args[4].split(" ")[0]
	if cmd == "gcalc":
	        try:
	                query = args[4][6:]
	                query = urllib.urlencode({'q':query})
	        except:
	                c.privmsg(args[5], "Error: no query specified.")
	                return
	        start = '<h2 class=r style="font-size:138%"><b>'
	        end = '</b>'
	        google = httplib.HTTPConnection("www.google.com")
	        google.request("GET","/search?"+query+"&num=1")
	        search = google.getresponse()
	        data = search.read()
	        #print data

	        if data.find(start) == -1:
	                c.privmsg(args[5], "Google Calculator results not found.")
	                return
	        else:
	                begin = data.index(start)
	                result = data[begin+len(start):begin+data[begin:].index(end)]
	                result = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace("\xa0",",")
	                c.privmsg(args[5], result)




