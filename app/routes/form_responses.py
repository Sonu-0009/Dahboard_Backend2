from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Request
from app.config.database import get_db
from app.schemas.form_responses import FormResponseSubmit
from app.models import form_responses as responses_model

router = APIRouter(prefix="/form_responses", tags=["FormResponses"])


def require_logged_in(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")


def require_role(request: Request, *roles: str):
    require_logged_in(request)
    role = request.session.get("role")
    if role not in roles:
        raise HTTPException(status_code=403, detail=f"Requires role: {roles}")


@router.post("/submit", summary="User submits responses to a form")
async def submit_response(payload: FormResponseSubmit, request: Request):
    require_role(request, "user")
    # Validate form exists
    form = responses_model.find_form(payload.form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Check if user already submitted to this form
    if responses_model.user_already_submitted(payload.form_id, request.session["user_id"]):
        raise HTTPException(
            status_code=400,
            detail="You have already submitted a response to this form",
        )

    # Optional validation against form questions
    try:
        responses_model.validate_answers_against_form(form, payload.answers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return responses_model.insert_response(payload.form_id, request.session["user_id"], payload.answers)


@router.get("/{form_id}/my", summary="User: view my submissions for a form")
async def my_submissions(form_id: str, request: Request):
    require_role(request, "user")
    # Form existence check
    if not responses_model.find_form(form_id):
        raise HTTPException(status_code=404, detail="Form not found")

    items = responses_model.list_user_submissions(form_id, request.session["user_id"])
    return {"items": items}

