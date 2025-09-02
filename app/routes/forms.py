# app/routes/forms.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Request
from app.config.database import get_db
from app.schemas.forms import FormCreate, Pagination, Question
from app.models import forms as forms_model

router = APIRouter(prefix="/forms", tags=["Forms"])

# ---------- helpers

def require_logged_in(request: Request):
    """
    Ensures there is a logged-in session.
    """
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="Login required")

def require_role(request: Request, *roles: str):
    """
    Ensures current session role is one of the allowed roles.
    """
    require_logged_in(request)
    role = request.session.get("role")
    if role not in roles:
        raise HTTPException(status_code=403, detail=f"Requires role: {roles}")

def is_super_admin(request: Request) -> bool:
    """
    Returns True if current user is super_admin.
    """
    return request.session.get("role") == "super_admin"

def ensure_owner_or_super(form_doc: Dict[str, Any], request: Request):
    """
    Ensures the requester is the form owner or super_admin.
    """
    if is_super_admin(request):
        return
    if not form_doc or str(form_doc.get("created_by")) != request.session.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized for this form")

def normalize_question_ids(questions: List[Question]) -> List[Dict[str, Any]]:
    """
    Ensures every question has a stable id (q1, q2, ... if missing).
    """
    normalized: List[Dict[str, Any]] = []
    auto_index = 1
    for q in questions:
        qid = q.id or f"q{auto_index}"
        auto_index += 1 if not q.id else 0
        item = q.dict()
        item["id"] = qid
        normalized.append(item)
    return normalized

# ---------- endpoints

@router.post("", summary="Create a new form (admin/super_admin only)")
async def create_form(payload: FormCreate, request: Request):
    """
    Creates a form owned by the logged-in admin or super_admin.
    """
    require_role(request, "admin", "super_admin")
    doc = {
        "title": payload.title,
        "description": payload.description,
        "questions": [q.dict() for q in payload.questions],
        "created_by": request.session["user_id"],
    }
    return forms_model.create_form(doc)

@router.get("", summary="List forms for current admin; super_admin sees all")
async def list_forms(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Optional title contains filter"),
):
    """
    Returns paginated forms. Admin: only their own. Super_admin: all.
    """
    require_role(request, "admin", "super_admin")
    filters: Dict[str, Any] = {}
    if not is_super_admin(request):
        filters["created_by"] = request.session["user_id"]
    if search:
        filters["title"] = {"$regex": search, "$options": "i"}
    items, total = forms_model.list_forms(filters, page, page_size)
    return {"items": items, "pagination": Pagination(total=total, page=page, page_size=page_size)}

@router.get("/{form_id}", summary="Get a form (admin owner or super_admin)")
async def get_form(form_id: str, request: Request):
    """
    Returns a single form structure if caller is owner or super_admin.
    """
    require_role(request, "admin", "super_admin")
    form = forms_model.get_form_by_id(form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    ensure_owner_or_super(form, request)
    return form

@router.delete("/{form_id}", summary="Delete form and cascade delete responses")
async def delete_form(form_id: str, request: Request):
    """
    Deletes a form (owner/super_admin) and all its responses (cascade).
    """
    require_role(request, "admin", "super_admin")
    form = forms_model.get_form_by_id(form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    ensure_owner_or_super(form, request)
    return forms_model.delete_form_and_responses(form_id)

# ---------- responses

 

@router.get("/{form_id}/summary", summary="Admin owner/super_admin: form + responses")
async def form_summary(
    form_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """
    Returns form structure and a paginated list of responses.
    """
    require_role(request, "admin", "super_admin")
    db = get_db()

    form = db.forms.find_one({"_id": ObjectId(form_id)})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    ensure_owner_or_super(form, request)

    total = db.form_responses.count_documents({"form_id": form_id})
    cursor = (
        db.form_responses.find({"form_id": form_id})
        .sort("submitted_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    responses: List[Dict[str, Any]] = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        responses.append(r)

    form["_id"] = str(form["_id"])
    return {
        "form": form,
        "responses": responses,
        "pagination": Pagination(total=total, page=page, page_size=page_size),
    }

