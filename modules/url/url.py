# This module implements some URL helpers

from ..module import Module

import re
import urllib2
import HTMLParser

def is_url(text):
    return False # TODO: filter non-urls somehow

class TitleParser(HTMLParser.HTMLParser):
    title = False
    title_text = "No title found"

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.title = False

    def handle_data(self, data):
        if self.title:
            self.title_text = data

class url(Module):
    def __init__(self, scrap):
        super(url, self).__init__(scrap)

        scrap.register_event("url", "pubmsg", self.distribute)
        scrap.register_event("url", "pubmsg", self.url_monitor)

        self.register_cmd("urlinfo", self.urlinfo_handler)

        self.title_parser = TitleParser()

    def url_monitor(self, server, event, bot):
        tokens = event.arguments[0].split()
        if tokens[0] == server.cmdchar + "urlinfo":
            return

        for token in tokens:
            if is_url(token):
                self.urlinfo(server, event, token)


    def urlinfo_handler(self, server, event, bot):
        for url in event.arg:
            self.urlinfo(server, event, url)

    def urlinfo(self, server, event, url):
        if "://" not in url:
            url = "http://"+url
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as e:
            server.reply(event, "URL fetch for %s failed: %s" % (url, e.reason))
            return
        except ValueError as e:
            server.reply(event, "URL fetch for %s failed: %s" % (url, e.message))
            return
        content = response.read()
        self.title_parser.feed(content)
        server.reply(event, "Title: %s" % self.title_parser.title_text)
        self.title_parser.title_text = "Title not found"
