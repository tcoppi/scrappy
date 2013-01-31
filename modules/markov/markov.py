#markov module for scrappy

#the inspiration for this code comes from
#"The Practice of Programming", so some of the variable
#names and such will be similar.

import random
import pickle
import re
import threading
import logging

from module import Module

class markov(Module):
    def __init__(self,scrap):
        super(markov, self).__init__(scrap)
        self.last = ""

        self.nickmatch = None
        self.statetab = {}
        self.lock = None
        self.w1 = "\n"
        self.w2 = "\n"

        self.lock = threading.Lock()
        scrap.autorep = True
        scrap.talk = True

        scrap.register_event("markov,", "msg", self.distribute)
        scrap.register_event("markov", "msg", self.markov_learn)

        self.register_cmd("markov_file", self.markov_file)
        self.register_cmd("talk", self.markov_talk)
        self.register_cmd("mkdump", self.markov_dump)
        self.register_cmd("mkload", self.markov_load)
        self.register_cmd("stats", self.markov_stats)
#    scrap.register_event("markov", "msg", tweet)

        self.nickmatch = re.compile(scrap.servers.itervalues().next()['nickname'])

        self.logger = logging.getLogger("scrappy.markov")
        random.seed()

    def markov_stats(self, server, event, bot):
        c = server["connection"]

        c.privmsg(event.target, "chains: %d" % len(self.statetab.items()))


    #loads in a previously pickled saved state
    def markov_load(self, server, event, bot):
        c = server["connection"]

        fp = event.cmd.split(" ")[1]

        self.lock.acquire()
        try:
            pkfile = open(fp, "r")
            self.statetab = pickle.load(pkfile)
            c.privmsg(event.target, "Loaded %s." % fp)
        except IOError:
                c.privmsg(event.target, "Could not load '%s': Doesn't exist\n" % fp)

        self.lock.release()


    #pickles out the state to a file
    def markov_dump(self, server, event, bot):
        c = server["connection"]
        self.lock.acquire()

        fp = event.cmd.split(" ")[1]

        pkfile = open(fp, "w+")

        pickle.dump(self.statetab, pkfile)
        c.privmsg(event.target, "Done taking a dump.")

        self.lock.release()

    def markov_file(self, server, event, bot):
        c = server["connection"]
        """Load a plaintext file."""
        mfname = event.cmd.split(" ")[1]

        self.lock.acquire()
        try:
            mf = open(mfname, 'r')
        except IOError:
            c.privmsg(event.target, "Error loading file %s." % mfname)
            self.lock.release()
            return

        c.privmsg(event.target, "%s successfully opened.  Reading..." % mfname)
        for line in mf.readlines():
            words = [x.strip() for x in line.split(" ") if not x.isspace()]
            if len(words) <= 1:
                #self.lock.release()
                continue

            w1 = w2 = "\n"

            for w in words:
                self.statetab.setdefault((w1, w2), []).append(w)
                w1, w2 = w2, w

            self.statetab.setdefault((w1, w2), []).append("\n")

        c.privmsg(event.target, "Done!")
        mf.close()
        self.lock.release()

        self.lock.acquire()
        pkfile = open("%s.mk" % mf, "w+")

        pickle.dump(self.statetab, pkfile)
        self.lock.release()


    def markov_learn(self, server, event, bot):
        """ Should not be called directly """

        self.logger.info("in learn")
        c = server["connection"]
        if event.cmd.startswith(event.cmdchar):
            return
        if event.cmd == "talk" or event.cmd == "markov_stats" or event.cmd == "mkload" or event.cmd == "mkdump" or event.cmd == "markov_file":
            return

        self.lock.acquire()

        words = [x.strip() for x in event.cmd.split(" ") if not x.isspace()]
        if len(words) <= 1:
            self.lock.release()
            return

        w1 = w2 = "\n"

        #go through every word and put them in a hash table.
        #EX the sentence "Mary had a little lamb"
        #first iteration, w1 and w2 are both empty.
        #statetab[w1][w2] doesn't exist, so make it and set
        #statetab[""][""] to Mary.
        #
        #Then, set w1 to w2 and w2 to i, so the chain moves forward.
        for i in words:
            self.statetab.setdefault((w1, w2), []).append(i)
            w1, w2 = w2, i

        self.statetab.setdefault((w1, w2), []).append("\n")

        if self.nickmatch.search(event.cmd) and bot.autorep == 1:
            tmp = self.emit_chain(random.choice(event.cmd.split(" ")))

            if len(tmp) <= 2:
                self.lock.release()
                return

            c.privmsg(event.target, "%s: %s" % (event.nick, tmp))
            self.lock.release()
            return

        #randomly reply
        if random.randint(0, 7) == 0 and bot.talk == 1:
            c.privmsg(event.target, "%s" %
                    (self.emit_chain(random.choice(event.cmd.split(" ")))))

        self.lock.release()

    def emit_chain(self, key):
        self.logger.info("in self.emit_chain")
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
                newword = random.choice(self.statetab[(w1, w2)]).strip()
            except KeyError:
                last = retval
                return retval


            retval = retval + newword + " "
            w1, w2 = w2, newword

            i = i + 1

            #max of rand words if we don't hit a space or other error
            if i >= random.randint(5, 50):
                last = retval
                return retval
        last = retval
        return retval

    def markov_talk(self, server, event, bot):
        """ Makes the markov chain talk to you """
        self.logger.info("in talk")

        c = server["connection"]
        try:
            key = random.choice([event.cmd.split(" ")[1].upper(), event.cmd.split(" ")[1].lower()])
        except IndexError:
            key = " "

        tmp = self.emit_chain(key)
        if len(tmp) <= 2:
            return
        if len(tmp.split()) <= 1:
            tmp = self.emit_chain(" ")
        last = ("%s %s" % (key, tmp)).lstrip()
        c.privmsg(event.target, ("%s %s" % (key, tmp)).lstrip())



#def tweet(server, args, bot):
#    c = server["connection"]
#    cmd = args[4].split(" ")[0]

#    if cmd == "tweet":
        #consumer_key = 'N2q3Owp3hRqDebYcoJN0Q'
        #consumer_secret = 'fEwVrTWDJYAnDMDduI2RsVLnyMIAvmfHeYt7HAuzE'
        #access_token_key = '21156817-VFyeze14zS3K9PrLQiXkgmvBOxorbNrAJyNwW09IQ'
        #access_token_secret = 'nK7Gr7JRyUl7E4cM4EyBUq6bIEG8g0VuzimurtOyI'

#        api = twitter.Api('N2q3Owp3hRqDebYcoJN0Q',
#                          'fEwVrTWDJYAnDMDduI2RsVLnyMIAvmfHeYt7HAuzE',
#                          "21156817-VFyeze14zS3K9PrLQiXkgmvBOxorbNrAJyNwW09IQ",
#                          'nK7Gr7JRyUl7E4cM4EyBUq6bIEG8g0VuzimurtOyI')
#        api.PostUpdate(last)
#        c.privmsg(args[5], "Updated Twitter with message: %s" % last)
