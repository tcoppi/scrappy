import peewee
# needed for init
import json
import urllib2

from module import DBModel

JSON_LOCATION = "https://raw.githubusercontent.com/samurailink3/hangouts-against-humanity/master/source/data/cards.js"

class Cards(DBModel):
    color = peewee.TextField()
    body = peewee.TextField()

def init_db():
    try:
        card_json = urllib2.urlopen(JSON_LOCATION)
    except URLError:
        return "Couldn't fetch cards file."
    card_json = card_json.read().replace("masterCards = ","")
    try:
        cards = json.loads(card_json)
    except ValueError:
        return "Couldn't parse cards JSON."
    massaged_dicts = [{'color':'white' if card["cardType"]=='A' else 'black', 'body':card["text"]} for card in cards]
    Cards.insert_many(massaged_dicts).execute()
    return "Successfully grabbed cards."
