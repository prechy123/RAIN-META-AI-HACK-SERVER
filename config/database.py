from pymongo import MongoClient
from config.conf import settings
import certifi

MONGO_URL = settings.MONGO_URL

# Use certifi for SSL certificate verification on macOS
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())

db = client.application

user_collection = db['user']
business_collection = db['business']
session_collection = db['session']