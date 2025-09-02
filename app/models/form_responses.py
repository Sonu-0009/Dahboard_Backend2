from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId

from app.config.database import get_db


def find_form(form_id: str) -> Dict[str, Any] | None:
    db = get_db()
    return db.forms.find_one({"_id": ObjectId(form_id)})


def user_already_submitted(form_id: str, user_id: str) -> bool:
    db = get_db()
    existing = db.form_responses.find_one({"form_id": form_id, "user_id": user_id})
    return existing is not None


def validate_answers_against_form(form_doc: Dict[str, Any], answers: Dict[str, Any]) -> None:
    qmap = {q["id"]: q for q in form_doc.get("questions", [])}
    for qid, ans in answers.items():
        if qid not in qmap:
            raise ValueError(f"Unknown question id: {qid}")
        qtype = qmap[qid]["type"]
        if qtype == "radio":
            if ans not in (qmap[qid].get("options") or []):
                raise ValueError(f"Invalid option for {qid}")
        if qtype == "checkbox":
            if not isinstance(ans, list) or any(a not in (qmap[qid].get("options") or []) for a in ans):
                raise ValueError(f"Invalid checkbox list for {qid}")


def insert_response(form_id: str, user_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    doc = {
        "form_id": form_id,
        "user_id": user_id,
        "answers": answers,
        "submitted_at": datetime.utcnow(),
    }
    result = db.form_responses.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


def list_user_submissions(form_id: str, user_id: str) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = (
        db.form_responses.find({"form_id": form_id, "user_id": user_id})
        .sort("submitted_at", -1)
    )
    items: List[Dict[str, Any]] = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        items.append(r)
    return items

