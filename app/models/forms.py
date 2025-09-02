from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId

from app.config.database import get_db


def normalize_question_ids(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    auto_index = 1
    for q in questions:
        qid = q.get("id") or f"q{auto_index}"
        auto_index += 1 if not q.get("id") else 0
        item = dict(q)
        item["id"] = qid
        normalized.append(item)
    return normalized


def create_form(doc: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    now = datetime.utcnow()
    doc = dict(doc)
    doc["questions"] = normalize_question_ids(doc.get("questions", []))
    doc["created_at"] = now
    doc["updated_at"] = now
    result = db.forms.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


def list_forms(filters: Dict[str, Any], page: int, page_size: int) -> Tuple[List[Dict[str, Any]], int]:
    db = get_db()
    total = db.forms.count_documents(filters)
    cursor = (
        db.forms.find(filters)
        .sort("created_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    items: List[Dict[str, Any]] = []
    for f in cursor:
        f["_id"] = str(f["_id"])
        items.append(f)
    return items, total


def get_form_by_id(form_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    form = db.forms.find_one({"_id": ObjectId(form_id)})
    if not form:
        return None
    form["_id"] = str(form["_id"])
    return form


def delete_form_and_responses(form_id: str) -> Dict[str, int]:
    db = get_db()
    res_forms = db.forms.delete_one({"_id": ObjectId(form_id)})
    res_responses = db.form_responses.delete_many({"form_id": form_id})
    return {
        "deleted_form_count": res_forms.deleted_count,
        "deleted_response_count": res_responses.deleted_count,
    }

