from datetime import datetime
from elasticsearch import Elasticsearch
import json, random
es = Elasticsearch()


with open('open-beer-database.json') as json_file:
    data = json.load(json_file)
    for p in data:
        try:
            fields = p['fields']   
            doc = {
                'name': fields['name'],
                'country': fields['country'],
                'price': (random.random() * 10),
                'city': fields['city'],
                'name_breweries': fields['name_breweries'],
            }
            es.index(index="beers", id=p['recordid'], body=doc)
        except:
            print("Could not index document")