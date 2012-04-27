import feedparser

steamURL = "http://store.steampowered.com/feeds/news.xml"

def init(bot):
	bot.register_event("steamdeal", "msg", steamdeal)
	
def steamdeal(c, args, bot):
	cmd = args[4].split(" ")[0]
	if cmd == "steamdeal":
	        feed = feedparser.parse(steamURL)
	        ret = feed["items"][0:10]
	        for x in ret:
	                if x["title"].find("Daily Deal") >= 0:
	                        ret = "%s (%s)" % (x["title"], x["link"])
	                        break
			
		c.privmsg(args[5], ret)
