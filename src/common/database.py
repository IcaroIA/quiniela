import pymongo


class Database(object):

    #URI = "mongodb://127.0.0.1:27017"
    URI = "mongodb+srv://IcaroIA:JY5W9K3PpwM12Rj7@quiniela-nxvjx.gcp.mongodb.net/test?retryWrites=true&w=majority"

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI, maxPoolSize=50, connect=False)
        Database.DATABASE = client['qnfl']

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
