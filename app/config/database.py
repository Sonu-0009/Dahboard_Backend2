import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None

def get_db():
    """
    Returns a singleton MongoDB database connection and ensures key indexes.
    """
    global _client, _db
    if _db is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        dbname = os.getenv("MONGO_DB", "Anuvadini")
        _client = MongoClient(uri)
        _db = _client[dbname]

        # ✅ Ensure indexes for existing collections
        _db.users.create_index("email", unique=True)
        _db.users_chat.create_index("user_id", unique=True)
        _db.guest_chat.create_index("guest_id", unique=True)

        # ✅ New: indexes for forms & responses
        # forms: list quickly by creator, and fetch by _id (implicit)
        _db.forms.create_index([("created_by", ASCENDING)])
        _db.forms.create_index([("title", ASCENDING)])

        # form_responses: fast by form, fast by user, sorted by time
        _db.form_responses.create_index([("form_id", ASCENDING)])
        _db.form_responses.create_index([("user_id", ASCENDING)])
        _db.form_responses.create_index([("form_id", ASCENDING), ("submitted_at", DESCENDING)])
        _db.form_responses.create_index([("form_id", ASCENDING), ("user_id", ASCENDING)])

    return _db