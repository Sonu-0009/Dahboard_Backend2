from fastapi import APIRouter, HTTPException, Request
from app.models.chat import save_message, get_chat_history
from app.schemas.chat import ChatMessage

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message")
async def add_message(request: Request, data: ChatMessage):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")

    user_id = request.session["user_id"]
    chat = save_message(user_id, data.role, data.text)

    return {"status": "saved", "message": chat}


@router.get("/history")
async def fetch_history(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")

    user_id = request.session["user_id"]
    messages = get_chat_history(user_id)

    return {"messages": messages}