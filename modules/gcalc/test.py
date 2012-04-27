import urllib, httplib

def gcalc():
        #cmd = args[4].split(" ")[0]
	#if cmd == "gcalc":
	       # try:
	             #query = args[4].split(" ")[1:]
	        query = urllib.urlencode({'q':"2+2"})
	                #c.privmsg(args[5], "Query: %s" % query)
	        #except:
	                #c.privmsg(args[5], "Error: no query specified.")
	                #return
	        start = '<h2 class=r style="font-size:138%"><b>'
	        end = '</b>'
	        google = httplib.HTTPConnection("www.google.com")
	        google.request("GET","/search?"+query+"&num=1")
	        search = google.getresponse()
	        data = search.read()
	        #print data
	        
	        if data.find(start) == -1: 
	                print "Google Calculator results not found."
	                return
	        else:
	                begin = data.index(start)
	                result = data[begin+len(start):begin+data[begin:].index(end)]
	                result = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace("\xa0",",")
	                print result
	              
if __name__=="__main__":
        gcalc()
