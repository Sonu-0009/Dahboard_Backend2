from fastapi import APIRouter, HTTPException, Request
from app.models.users_chat import save_message, get_chat_history
from app.schemas.users_chat import ChatMessage

router = APIRouter(prefix="/users_chat", tags=["Users Chat"])

# Placeholder for your AI bot function
def generate_bot_response(user_text: str) -> str:
    # Replace this with your real AI model call
    return f"Bot reply to: {user_text}"

@router.post("/message")
async def add_message(request: Request, data: ChatMessage):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")

    user_id = request.session["user_id"]

    # 1️⃣ Save the user's message
    save_message(user_id, "user", data.text)

    # 2️⃣ Generate bot response
    bot_text = generate_bot_response(data.text)

    # 3️⃣ Save bot response
    save_message(user_id, "bot", bot_text)

    return {"status": "saved", "bot_response": bot_text}

@router.get("/history")
async def fetch_history(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")

    user_id = request.session["user_id"]
    messages = get_chat_history(user_id)
    return {"messages": messages}