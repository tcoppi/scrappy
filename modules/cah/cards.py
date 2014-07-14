import peewee
# needed for init
import json
import urllib2
import HTMLParser

from module import DBModel

JSON_LOCATION = "https://raw.githubusercontent.com/samurailink3/hangouts-against-humanity/master/source/data/cards.js"


class Cards(DBModel):
    color = peewee.TextField()
    body = peewee.TextField()
    drawn = peewee.BooleanField(default=False)
    num_answers = peewee.IntegerField()

class NoMoreCards(Exception):
    pass

class Deck(object):
    def __init__(self):
        self.shuffle()
        self.htmlParser = HTMLParser.HTMLParser()

    def shuffle(self):
        Cards.update(drawn=False).execute()

    def draw(self, color):
        try:
            card = Cards.select().where(Cards.color==color, Cards.drawn==False).order_by(peewee.fn.Random()).get()
        except Cards.DoesNotExist as e:
            raise NoMoreCards('No more %s cards' % color)
        card.update(drawn=True).where(Cards.id == card.id).execute()
        
        card.body = self.htmlParser.unescape(card.body)
        return card

    def count(self, color):
        return Cards.select().where(Cards.drawn==False, Cards.color==color).count()


def init_db():
    try:
        card_json = urllib2.urlopen(JSON_LOCATION)
    except urllib2.URLError:
        return "Couldn't fetch cards file."
    card_json = card_json.read().replace("masterCards = ","")
    try:
        cards = json.loads(card_json)
    except ValueError:
        return "Couldn't parse cards JSON."
    massaged_dicts = [{'color':'white' if card["cardType"]=='A' else 'black', 'body':card["text"], 'num_answers':int(card["numAnswers"])} for card in cards]
    for card in massaged_dicts:
        add_card(card["color"], card["body"], card["num_answers"])
    return "Successfully grabbed cards."

def add_card(color, body, num_answers):
    Cards.insert(color=color, body=body, num_answers=num_answers).execute()
