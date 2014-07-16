from ..module import Module
import urllib2
import json
import math

irc_color_map = {
    "FFFFFF":"1,0", # white
    "000000":"0,1", # black, white fg
    "00008B":"0,2", # darkblue, white fg
    "008000":"1,3", # green
    "FF0000":"1,4", # red
    "8B0000":"0,5", # darkred, white fg
    "800080":"1,6", # purple
    "FFA500":"1,7", # orange
    "FFFF00":"1,8", # yellow
    "32CD32":"1,9", # limegreen
    "008080":"1,10", # teal
    "ADD8E6":"1,11", # lightblue
    "0000FF":"1,12", # blue
    "FF69B4":"1,13", # hotpink
    "808080":"1,14", # gray
    "D3D3D3":"1,15" # lightgrey
}

def color_distance(c1, c2):
    c1 = c1[-6:] # strip any leading characters, 0x or #
    c2 = c2[-6:]
    r1 = int(c1[0:2],16)
    g1 = int(c1[2:4],16)
    b1 = int(c1[4:6],16)
    r2 = int(c2[0:2],16)
    g2 = int(c2[2:4],16)
    b2 = int(c2[4:6],16)
    return math.sqrt(math.pow(r2-r1,2)+math.pow(g2-g1,2)+math.pow(b2-b1,2))

def closest_color(hex_color):
    return min(irc_color_map.keys(), key=lambda x: color_distance(x, hex_color))

def closest_irc_color(hex_color):
    return irc_color_map[closest_color(hex_color)]

def color_text(text, color):
    return "\x03%s%s\x03" % (color, text)

#TODO: paginate
class github(Module):

    def __init__(self, scrap):
        super(github, self).__init__(scrap)
        scrap.register_event("github", "msg", self.distribute)

        self.register_cmd("gh-issues", self.get_issues)

    def get_issues(self, server, event, bot):
        repo = event.arg[0]


        baseurl = "https://api.github.com"
        url = baseurl+"/repos/%s/issues" % repo

        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as e:
            server.privmsg(event.target, "Problems accessing the Github API, try again later"+str(e))
            return
        #check response.info for important information like rate limits
        response = response.read()
        response = json.loads( response )
        if len(response) == 0:
            server.privmsg(event.target, "No open issues for %s" % repo)
        else:
            # Get labels
            label_colors = {} # key name, value color (IRC color, not hex)
            for issue in response:
                num = issue["number"]
                title = issue["title"]
                user = issue["user"]["login"]
                labels = issue["labels"]
                colored_labels = []
                for label in labels:
                    name = label["name"]
                    if name not in label_colors:
                        label_colors[name] = closest_irc_color(label["color"])

                    color = label_colors[name]
                    colored_labels.append(color_text(name, color))
                label_str = "|".join(colored_labels)
                if issue["assignee"]:
                    assigned_to = issue["assignee"]["login"]
                else:
                    assigned_to = None

                server.privmsg(event.target, "Issue %d %s - opened by %s, assigned to %s - %s" % (num, label_str, user, assigned_to, title))

