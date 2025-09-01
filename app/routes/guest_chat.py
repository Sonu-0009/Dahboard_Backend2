from fastapi import APIRouter
from app.models.guest_chat import save_message, get_chat_history
from app.schemas.guest_chat import ChatMessage

router = APIRouter(prefix="/guest_chat", tags=["Guest Chat"])

# Dummy bot response (replace with your AI model later)
def generate_bot_response(user_text: str) -> str:
    return f"Bot reply to: {user_text}"

# 1️⃣ Save user message + bot response
@router.post("/message/{guest_id}")
async def add_message(guest_id: str, data: ChatMessage):
    # Save user message
    save_message(guest_id, "user", data.text)

    # Generate + save bot response
    bot_text = generate_bot_response(data.text)
    save_message(guest_id, "bot", bot_text)

    return {"status": "saved", "bot_response": bot_text}

# 2️⃣ Fetch history
@router.get("/history/{guest_id}")
async def fetch_history(guest_id: str):
    messages = get_chat_history(guest_id)
    return {"messages": messages}
