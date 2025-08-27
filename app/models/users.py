from app.config.database import get_db
from bson import ObjectId

class UserModel:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.users

    def create_user(self, doc: dict) -> str:
        res = self.col.insert_one(doc)
        return str(res.inserted_id)

    def find_by_email(self, email: str):
        return self.col.find_one({"email": email})

    def find_by_id(self, user_id: str):
        return self.col.find_one({"_id": ObjectId(user_id)})