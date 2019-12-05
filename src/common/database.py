import pymongo
import os


class Database(object):

    #URI = "mongodb://127.0.0.1:27017"
    #URI = "mongodb+srv://IcaroIA:{}@quiniela-nxvjx.gcp.mongodb.net/test?retryWrites=true&w=majority".format(os.environ.get('MONGO'))
    URI = os.environ.get("MONGOLAB_URI")

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['heroku_m3kb061z']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def find_ord(collection, query, order):
        return Database.DATABASE[collection].find(query).sort(order, pymongo.DESCENDING)
