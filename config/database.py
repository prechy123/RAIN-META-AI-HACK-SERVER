from pymongo import MongoClient
from config.conf import settings

MONGO_URL = settings.MONGO_URL

client = MongoClient(MONGO_URL)

db = client.application

user_collection = db['user']
business_collection = db['business']
session_collection = db['session']