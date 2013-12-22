import os
import os.path
import subprocess

from ..module import Module

class git(Module):
    def __init__(self, scrap):
        super(git, self).__init__(scrap)
        scrap.register_event("git", "msg", self.distribute)
        self.register_cmd("version", self.git_version)
        self.register_cmd("update", self.update)

    def git_version(self, server, event, bot):
        if not os.path.exists(".git"):
            server.privmsg(event.target, "Scrappy not running from a git repo")
        else:
            ver = subprocess.check_output(["git", "describe", "--always"])
            server.privmsg(event.target, "Scrappy git version: %s" % ver.strip())

    def update(self, server, event, bot):
        if not os.path.exists(".git"):
            server.privmsg(event.target, "Scrappy not running from a git repo")
        else:
            output = subprocess.check_output(["git", "pull"])
            if "up-to-date" in output:
                server.privmsg(event.target, "Scrappy is already the latest version")
            else:
                server.privmsg(event.target, "Scrappy updated! You may need to %sreboot." % server.cmdchar)
                self.git_version(server, event, bot)



