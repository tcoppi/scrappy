from module import Module

class reverse(Module):
    def __init__(self, scrap):
        print "reverse loading"
        super(reverse, self).__init__(scrap)

        scrap.register_event("reverse", "msg", self.distribute)

        self.register_cmd("reverse", self.reverse)

    def reverse(self, server, event, bot):
        """Takes a string and reverses it.  Simple."""

        if len(event.tokens) < 2:
            server.privmsg(event.target, "Not enough arguments")
            return

        if len(event.arg) > 0:
            # Squishes all the whitespace. oh well.
            rev = list(" ".join(event.arg))
            rev.reverse()
            strng = ''.join(rev)
        else:
            strng = "?tahw esreveR"

        server.privmsg(event.target, strng)
