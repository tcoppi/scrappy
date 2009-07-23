#markov module for scrappy

#the inspiration for this code comes from
#"The Practice of Programming", so some of the variable
#names and such will be similar.

#i'm not sure if this is thread safe

import random
import cPickle
import re

nickmatch = None
urlmatch = None
statetab = {}

w1 = w2 = "\n"

def __init__(scrap):
    global nickmatch
    global urlmatch

    scrap.register_msg_event(markov_learn)
    scrap.register_msg_event(markov_talk)
    scrap.register_msg_event(markov_load)
    scrap.register_msg_event(markov_dump)
    scrap.register_msg_event(markov_stats)

    nickmatch = re.compile(scrap.nickname)
    urlmatch = re.compile("http")

    random.seed()

def markov_stats(c, list, bot):
    global statetab

    cmd = list[4].split(" ")[0]

    if cmd == "markov_stats":
        c.privmsg(list[5], "words: %d" % len(statetab[("\n","\n")]))
        c.privmsg(list[5], "chains: %d" % len(statetab.items()))

#loads in a previously pickled saved state
def markov_load(c, list, bot):
    global statetab

    cmd = list[4].split(" ")[0]

    if cmd == "mkload":
        fp = list[4].split(" ")[1]

        pkfile = open(fp, "r")

        statetab = cPickle.load(pkfile)

#pickles out the state to a file
def markov_dump(c, list, bot):
    global statetab

    cmd = list[4].split(" ")[0]

    if cmd == "mkdump":
        fp = list[4].split(" ")[1]

        pkfile = open(fp, "w+")

        cPickle.dump(statetab,pkfile)

def markov_learn(c, list, bot):
    """ Should not be called directly """

    words = [x for x in list[4].split(" ") if not x.isspace()]

    global statetab
    global urlmatch
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
        statetab.setdefault((w1, w2), []).append(i)
        w1, w2 = w2, i

    statetab.setdefault((w1, w2), []).append("\n")

    if nickmatch.search(list[4]) and bot.autorep == 1 and random.randint(0, 2) == 0:
        tmp = emit_chain(random.choice(list[4].split(" ")))

        if len(tmp) <= 2:
            return

        c.privmsg(list[5], "%s: %s" % (list[0], tmp))
        return

    #randomly reply
    if random.randint(0, 15) == 0 and bot.talk == 1:
        tmp = emit_chain(random.choice(list[4].split(" ")))
        if urlmatch.search(tmp):
            return
        c.privmsg(list[5], "%s" % tmp)

def emit_chain(key):
    global statetab
    global w1
    global w2

    i = 0

    w1 = w2 = "\n"

    newword = ""

    #make the first word the key if its not a space
#    if(key != " "):
#        retval = key + " "
#    else:
    retval = ""

    if key != " ":
        w2 = key

    while 1:
        try:
            newword = random.choice(statetab[(w1, w2)])
        except KeyError:
            return retval

        retval = retval + newword + " "
        w1, w2 = w2, newword

        if i == 0 and key != " ":
            retval = key + " " + retval

        i = i + 1

        #max of rand words if we don't hit a space or other error
        if i >= random.randint(5, 50):
            return retval

    return retval

def markov_talk(c, list, bot):
    """ Makes the markov chain talk to you """

    global tmp

    cmd = list[4].split(" ")[0]

    try:
        key = list[4].split(" ")[1]
    except IndexError:
        key = " "

    if list[3] and cmd == "talk":
        tmp = emit_chain(key)
        if len(tmp) <= 2:
            return

        if urlmatch.search(tmp):
            return
        else:
            c.privmsg(list[5], "%s" % tmp)
