import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        dbname = os.getenv("MONGO_DB", "Anuvadini")
        _client = MongoClient(uri)
        _db = _client[dbname]
        _db.users.create_index("email", unique=True)
    return _db