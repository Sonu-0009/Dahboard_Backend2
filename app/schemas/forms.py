# app/schemas/forms.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

QuestionType = Literal["text", "radio", "checkbox"]

class Question(BaseModel):
    """
    A single question config inside a form.
    """
    id: Optional[str] = Field(None, description="Stable question id (e.g. q1)")
    text: str
    type: QuestionType
    options: Optional[List[str]] = None  # for radio/checkbox

class FormCreate(BaseModel):
    """
    Payload to create a form.
    """
    title: str
    description: Optional[str] = None
    questions: List[Question]

class Pagination(BaseModel):
    """
    Generic pagination response envelope.
    """
    total: int
    page: int
    page_size: int

