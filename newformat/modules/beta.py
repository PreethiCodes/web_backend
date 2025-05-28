from pymongo import MongoClient
from dotenv import load_dotenv
import os


class BetaClass:
    def __init__(self):
        load_dotenv()
        self.connectionURI = os.getenv("MONGODB_URI")
        self.client = MongoClient(self.connectionURI)
        self.db = self.client["database-name"]
        self.collection = self.db["collection-name"]

    def simplygetalldata(self):
        data = self.collection.find()
        for record in data:
            print(record)

    def simplyinsert(self, data):
        result = self.collection.insert_one(data)
        print(f"Inserted document with ID: {result.inserted_id}")
