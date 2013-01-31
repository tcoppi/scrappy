from module import Module

class reverse(Module):
    def __init__(self, scrap):
        print "reverse loading"
        super(reverse, self).__init__(scrap)

        scrap.register_event("reverse", "msg", self.distribute)

        self.register_cmd("reverse", self.reverse)

    def reverse(self, server, event, bot):
        """Takes a string and reverses it.  Simple."""
        c = server["connection"]

        params = event.cmd.split(" ")[1:]
        if len(params) > 0:
            # Squishes all the whitespace. oh well.
            rev = list(" ".join(params))
            rev.reverse()
            strng = ''.join(rev)
        else:
            strng = "?tahw esreveR"

        c.privmsg(event.target, strng)
