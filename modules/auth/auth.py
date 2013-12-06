from module import Module

import utility.user.auth.google_oauth as google_oauth
import utility.user.user as user

class auth(Module):
    def __init__(self, scrap):
        super(auth, self).__init__(scrap)
        scrap.register_event("auth", "msg", self.distribute)
        self.register_cmd("auth", self.auth)
        self.register_cmd("isauth", self.is_auth)
        self.authenticator = google_oauth.Auth()

    def auth(self, server, event, bot):
        if len(event.arg) == 0:
           server.privmsg(event.source.nick, self.authenticator.challenge(event.source, server))

        elif len(event.arg) == 1:
            (success, msg) = self.authenticator.respond(event.source, server, event.arg[0])
            if success:
                server.privmsg(event.target, msg)
            else:
                server.privmsg(event.target, "Unable to authenticate: %s" % msg)
        else:
            server.privmsg(event.target, "Doin it wrong!")

    def is_auth(self, server, event, bot):
        if user.is_authenticated(event.source, server["servername"]):
            server.privmsg(event.target, "Yes, you're authenticated")
        else:
            server.privmsg(event.target, "No, you're not authenticated")
