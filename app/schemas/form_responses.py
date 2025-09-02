from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FormResponseSubmit(BaseModel):
    """
    Payload for users to submit answers.
    """
    form_id: str
    # answers map question_id -> value (str | List[str])
    answers: Dict[str, Any]


class FormResponse(BaseModel):
    """
    Form response as stored/returned.
    """
    id: Optional[str] = Field(None, alias="_id")
    form_id: str
    user_id: str
    answers: Dict[str, Any]
    submitted_at: datetime


class FormResponseList(BaseModel):
    items: List[FormResponse]

