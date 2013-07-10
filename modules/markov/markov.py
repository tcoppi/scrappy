#markov module for scrappy

#the inspiration for this code comes from
#"The Practice of Programming", so some of the variable
#names and such will be similar.

import random
import os.path
import pickle
import re
import threading
import time
import logging

from module import Module

class markov(Module):
    def __init__(self,scrap):
        super(markov, self).__init__(scrap)
        self.delay_mean = 10
        self.delay_stdev = 4
        self.nickmatch = None
        self.statetab = {}
        self.w1 = "\n"
        self.w2 = "\n"

        self.lock = threading.Lock()
        # Don't store this in scrap!?
        scrap.autorep = True
        scrap.talk = True

        scrap.register_event("markov", "msg", self.distribute)
        scrap.register_event("markov", "msg", self.markov_learn)

        self.register_cmd("talk", self.markov_talk)
        self.register_cmd("mkdump", self.markov_dump)
        self.register_cmd("mkload", self.markov_load)
        self.register_cmd("mkadd", self.markov_file)
#        self.register_cmd("markov_file", self.markov_file)
        self.register_cmd("mkstats", self.markov_stats)
        self.register_cmd("mkdelay", self.markov_delay)
#    scrap.register_event("markov", "msg", tweet)

        self.nickmatch = re.compile(scrap.servers.itervalues().next()['nickname'])

        random.seed()

    def markov_stats(self, server, event, bot):
        c = server["connection"]

        c.privmsg(event.target, "chains: %d" % len(self.statetab.items()))

    def markov_delay(self, server, event, bot):
        c = server["connection"]
        if len(event.tokens) < 3:
            c.privmsg(event.target, "Need a mean AND stdev as arguments.")

        try:
            self.delay_mean = float(event.tokens[1])
            self.delay_stdev = float(event.tokens[2])
            c.privmsg(event.target, "Delay is now N(%.2f,%.2f)" % (self.delay_mean, self.delay_stdev))
        except:
            c.privmsg(event.target, "I didn't like the format those were in, try again.")


    #loads in a previously pickled saved state
    def markov_load(self, server, event, bot):
        c = server["connection"]

        if len(event.tokens) < 2:
            c.privmsg(event.target, "Not enough arguments fo load.")
            return

        fp = event.tokens[1]

        with self.lock:
            try:
                pkfile = open(fp, "r")
                self.statetab = pickle.load(pkfile)
                c.privmsg(event.target, "Loaded %s." % fp)
            except IOError:
                c.privmsg(event.target, "Could not load '%s': Doesn't exist" % fp)

    #pickles out the state to a file
    def markov_dump(self, server, event, bot):
        c = server["connection"]

        if len(event.tokens) < 2:
            c.privmsg(event.target, "Not enough arguments fo dump.")
            return

        fp = event.tokens[1]

        with self.lock:

            pkfile = open(fp, "w+")
            pickle.dump(self.statetab, pkfile)
            c.privmsg(event.target, "Done taking a dump.")


    def markov_file(self, server, event, bot):
        """Load a plaintext file."""
        c = server["connection"]

        if len(event.tokens) < 2:
            c.privmsg(event.target, "Not enough arguments fo file.")

        mfname = event.tokens[1]

        try:
            valid_files = os.listdir('markov_input')
            if mfname not in valid_files:
                c.privmsg(event.target, "File %s doesn't exist." % mfname)
            size = os.path.getsize('markov_input/'+mfname)
            mf = open('markov_input/'+mfname, 'r')
        except IOError:
            c.privmsg(event.target, "Error loading file %s." % mfname)
            return

        c.privmsg(event.target, "%s successfully opened. Reading %d bytes..." % (mfname, size))
        start = time.time()
        for line in mf:
            cur_time = time.time()
            if cur_time-start > 10:
                start = cur_time
                c.privmsg(event.target, "Still loading, %d bytes left to go" % size)

            size -= len(line)

            self.learn_sentence(line.split())

        c.privmsg(event.target, "Done!")
        mf.close()

    def markov_learn(self, server, event, bot):
        """ Should not be called directly """
        start = time.time()
        # since this doesn't go via distribute, need to add some helpers
        event.tokens = event.arguments[0].split(" ")
        if not event.tokens:
            return
        if not event.tokens[0]:
            return
        event.arg = event.tokens[1:]
        event.command = event.tokens[0][1:]
        cmdchar = event.tokens[0][0]

        if cmdchar == server["cmdchar"]:
            return

#        if event.cmd == "talk" or event.cmd == "markov_stats" or event.cmd == "mkload" or event.cmd == "mkdump" or event.cmd == "markov_file":
#            return

        c = server["connection"]

        delay = random.gauss(self.delay_mean, self.delay_stdev)
        self.logger.debug("Reply delay N(%f,%f) is %f" % (self.delay_mean, self.delay_stdev, delay))

        if self.nickmatch.search(event.arguments[0]) and bot.autorep == 1:
            counter = 0
            tmp = []
            while len(tmp) <= 2 and counter < 10:
                tmp = self.emit_chain(random.choice(event.tokens))

                counter += 1

            if counter < 10:
                now = time.time()
                delta = now-start
                if delta < delay:
                    time.sleep(delay-delta)
                c.privmsg(event.target, "%s: %s" % (event.source.nick, " ".join(tmp)))

        #randomly reply
        if random.randint(0, 7) == 0 and bot.talk == 1:
            now = time.time()
            delta = now-start
            if delta < delay:
                time.sleep(delay-delta)
            self.last_talked = time.time()
            c.privmsg(event.target, "%s" %
                    (" ".join(self.emit_chain(random.choice(event.tokens)))))

        self.learn_sentence(event.tokens)

    def learn_sentence(self,tokens):
        """Feed me a tokenized sentence"""
        #self.logger.info("in learn")
        with self.lock:

            words = [x.strip() for x in tokens if not x.isspace()]
            if len(words) <= 1:
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
                w1, w2 = w2, i.lower()

            self.statetab.setdefault((w1, w2), []).append("\n")


    def emit_chain(self, key):
        i = 0

        w1 = w2 = "\n"

        newword = ""

        #make the first word the key if its not a space
#    if(key != " "):
#     retval = key + " "
#    else:
        retval = []

        w2 = key.lower()

        while 1:
            try:
                newword = random.choice(self.statetab[(w1, w2)]).strip()
            except KeyError:
                break

            retval.append(newword)
            w1, w2 = w2, newword

            i = i + 1

            #max of rand words if we don't hit a space or other error
            if i >= random.randint(5, 50):
                break

        return retval

    def markov_talk(self, server, event, bot):
        """ Makes the markov chain talk to you """
        self.logger.info("in talk")
        c = server["connection"]

        if len(event.tokens) < 2:
            try:
                key = random.choice(self.statetab[("\n","\n")])
            except KeyError:
                c.privmsg(event.target, "Don't wanna talk!")
                return
        else:
            key = event.tokens[1]

        tmp = []
        counter = 0
        while len(tmp) < 2 and counter < 10:
            tmp = self.emit_chain("\n")
            counter += 1

        if tmp:
            c.privmsg(event.target, ("%s %s" % (key, " ".join(tmp))).lstrip())



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
