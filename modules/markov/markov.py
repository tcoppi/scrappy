#markov module for scrappy

#the inspiration for this code comes from
#"The Practice of Programming", so some of the variable
#names and such will be similar.

import random
import pickle
import re
import threading


#EXPERIMENTAL
last = ""
import twitter

api = None
twitteruser = 'scrappybot'
twitterpass = 'scrappyb0t'
consumer_key = 'N2q3Owp3hRqDebYcoJN0Q'
consumer_secret ='fEwVrTWDJYAnDMDduI2RsVLnyMIAvmfHeYt7HAuzE'
access_token_key = 'access_token'
access_token_secret = 'access_token_secret'

nickmatch = None
statetab = {}
lock = None
w1 = w2 = "\n"


def init(scrap):
    global nickmatch
    global lock
    global api

    lock = threading.Lock()
    scrap.autorep = True
    scrap.talk = True

    scrap.register_event("markov", "msg", markov_learn)
    scrap.register_event("markov", "msg", markov_file)
    scrap.register_event("markov", "msg", markov_talk)
    scrap.register_event("markov", "msg", markov_load)
    scrap.register_event("markov", "msg", markov_dump)
    scrap.register_event("markov", "msg", markov_stats)
    #scrap.register_event("markov", "msg", tweet)

    nickmatch = re.compile(scrap.nickname)

    random.seed()
    
    #api = twitter.Api(username=twitteruser, password=twitterpass)
    #api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret)#, access_token_key=access_token, access_token_secret=access_token_secret)

def markov_stats(c,list,bot):
    global statetab

    cmd = list[4].split(" ")[0]

    if cmd == "markov_stats":
	c.privmsg(list[5], "words: %d" % len(statetab[("\n","\n")]))
	c.privmsg(list[5], "chains: %d" % len(statetab.items()))

#loads in a previously pickled saved state
def markov_load(c,list,bot):
	global statetab
	global lock

	cmd = list[4].split(" ")[0]

	if cmd == "mkload":
		fp = list[4].split(" ")[1]

		lock.acquire()
		try:
			pkfile = open(fp,"r")
			statetab = pickle.load(pkfile)
		except IOError:
			print "Could not load db: Doesn't exist\n"
	    
		lock.release()


#pickles out the state to a file
def markov_dump(c,list,bot):
    global statetab
    global lock

    lock.acquire()

    cmd = list[4].split(" ")[0]

    if cmd == "mkdump":
	fp = list[4].split(" ")[1]

	pkfile = open(fp,"w+")

	pickle.dump(statetab,pkfile)

    lock.release()

def markov_file(c, list, bot):
	"""Load a plaintext file."""
	cmd = list[4].split(" ")[0]

	if cmd == "markov_file": 
		global lock
		mfname = list[4].split(" ")[1]
		
		lock.acquire()
		try:
			mf = open(mfname, 'r')
		except IOError:
			c.privmsg(list[5], "Error loading file %s." % mfname)
			lock.release()
			return
			
		c.privmsg(list[5], "%s successfully opened.  Reading..." % mfname)	
		for line in mf.readlines():
			words = [x.strip() for x in line.split(" ") if not x.isspace()]
			if len(words) <= 1:
				lock.release()
				return
				
			global statetab
			global w1
			global w2
			
			w1 = w2 = "\n"
			
			for w in words:
				statetab.setdefault((w1, w2), []).append(w)
				w1, w2 = w2, w
				
			statetab.setdefault((w1, w2), []).append("\n")
			
		c.privmsg(list[5], "Done!")	
		mf.close()
		lock.release()
		
		lock.acquire()
		pkfile = open("%s.mk" % mf,"w+")
	
		pickle.dump(statetab,pkfile)
		lock.release()
		


def markov_learn(c,list,bot):
    """ Should not be called directly """
    global lock
    
    cmd = list[4].split(" ")[0]
    if cmd == "talk" or cmd == "markov_stats" or cmd == "mkload" or cmd == "mkdump":
	    return
    lock.acquire()

    words = [x.lower().strip() for x in list[4].split(" ") if not x.isspace()]
    if len(words) <= 1:
	    lock.release()
	    return

    global statetab
    global w1
    global w2

    w1 = w2 = "\n"

    #go through every word and put them in a hash table.
    #EX the sentence "Mary had a little lamb"
    #first iteration, w1 and w2 are both empty.
    #statetab[w1][w2] doesn't exist, so make it and set
    #statetab[""][""] to Mary.
    #
    #Then, set w1 to w2 and w2 to i, so the chain moves forward.
    for i in words:
	statetab.setdefault((w1,w2),[]).append(i)
	w1,w2 = w2, i

    statetab.setdefault((w1,w2),[]).append("\n")

    if nickmatch.search(list[4]) and bot.autorep == 1 and random.randint(0,10) == 0:
	tmp = emit_chain(random.choice(list[4].split(" ")))

	if len(tmp) <= 2:
		lock.release()
		return

	c.privmsg(list[5], "%s: %s" % (list[0],tmp))
	lock.release()
	return

    #randomly reply
    if random.randint(0,15) == 0 and bot.talk == 1:
	c.privmsg(list[5], "%s" % (emit_chain(random.choice(list[4].split(" ")))))

    lock.release()

def emit_chain(key):
    global statetab
    global w1
    global w2

    i = 0

    w1 = w2 = "\n"

    newword = ""

    #make the first word the key if its not a space
#    if(key != " "):
#	 retval = key + " "
#    else:
    retval = ""

    if key != " ":
	w2 = key

    while 1:
	try:
	    newword = random.choice(statetab[(w1,w2)]).strip()
	except KeyError:
	    return retval

	retval = retval + newword + " "
	w1,w2 = w2,newword

	i = i + 1

	#max of rand words if we don't hit a space or other error
	if i >= random.randint(5,50):
	    return retval

    return retval

def markov_talk(c,list,bot):
    """ Makes the markov chain talk to you """
    global last

    cmd = list[4].split(" ")[0]

    try:
	key = list[4].split(" ")[1].lower()
    except IndexError:
	key = " "

    if list[3] and cmd == "talk":
	tmp = emit_chain(key);
	if len(tmp) <= 2:
	    return
	if len(tmp.split()) <= 1:
		tmp = emit_chain(" ")
	last = tmp
	c.privmsg(list[5],("%s %s" % (key, tmp)).lstrip())
	
	
	
def tweet(c, args, bot):
	cmd = args[4].split(" ")[0]
	
	if cmd == "tweet":
		api.PostUpdate(last)
		c.privmsg(args[5], "Updated Twitter with message: %s" % last)
