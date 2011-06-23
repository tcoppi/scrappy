import socket
import cPickle

def init(bot):
    bot.register_event("url", "msg", url)

def url(c, args, bot):
    cmd = args[4].split(" ")[0]

    try:
        fp = open("urldb", "r+")
        db = cPickle.load(fp)
        fp.close()
    except:
        db = {}

    if cmd == "url":
        try:
            newurl = args[4].split(" ")[2]
            db[args[4].split(" ")[1]] = newurl

            fp = open("urldb", "w")
            cPickle.dump(db, fp)
            fp.close()

            c.privmsg(args[5], "Saved " + args[4].split(" ")[1] + " as " + newurl)
        except:
            # then we only have to look it up
            c.privmsg(args[5], db[args[4].split(" ")[1]])

