import os.path
import subprocess

from module import Module

class git(Module):
    def __init__(self, scrap):
        super(git, self).__init__(scrap)
        scrap.register_event("git", "msg", self.distribute)
        self.register_cmd("version", self.git_version)

    def git_version(self, server, event, bot):
        c = server["connection"]

        if not os.path.exists(".git"):
            c.privmsg(event.target, "Scrappy not running from a git repo")
        else:
            ver = subprocess.check_output(["git", "describe", "--always"])
            c.privmsg(event.target, "Scrappy git version: %s" % ver.strip())

