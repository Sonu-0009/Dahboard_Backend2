from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str   # "user" or "bot"
    text: str
    time: Optional[datetime] = None

class ChatHistory(BaseModel):
    guest_id: str
    messages: List[ChatMessage] = []
    last_updated: Optional[datetime] = None
