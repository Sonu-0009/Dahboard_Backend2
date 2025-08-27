from datetime import datetime
from typing import Dict, Any
from app.config.database import get_db

db = get_db()

def save_message(user_id: str, role: str, text: str) -> Dict[str, Any]:
    chat = {
        "role": role,
        "text": text,
        "time": datetime.utcnow()
    }

    db.chats.update_one(
        {"user_id": user_id},
        {"$push": {"messages": chat}, "$set": {"last_updated": datetime.utcnow()}},
        upsert=True
    )

    return chat

def get_chat_history(user_id: str):
    history = db.chats.find_one({"user_id": user_id}, {"_id": 0, "messages": 1})
    return history["messages"] if history else []