from module import Module
import urllib2
import json

#TODO: paginate
class github(Module):

    def __init__(self, scrap):
        super(github, self).__init__(scrap)
        scrap.register_event("github", "msg", self.distribute)

        self.register_cmd("gh-issues", self.get_issues)

    def get_issues(self, server, event, bot):
        c = server["connection"]
        repo = event.arg[0]


        baseurl = "https://api.github.com"
        url = baseurl+"/repos/%s/issues" % repo

        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as e:
            c.privmsg(event.target, "Problems accessing the Github API, try again later"+str(e))
            return
        #check response.info for important information like rate limits
        response = response.read()
        response = json.loads( response )
        if len(response) == 0:
            c.privmsg(event.target, "No open issues for %s" % repo)
        else:
            for issue in response:
                num = issue["number"]
                name = issue["title"]
                user = issue["user"]["login"]
                print issue["assignee"]
                if issue["assignee"]:
                    assigned_to = issue["assignee"]["login"]
                else:
                    assigned_to = None

                c.privmsg(event.target, "Issue %d - opened by %s, assigned to %s - %s" % (num, user, assigned_to, name))


        for key in response:
            print key


