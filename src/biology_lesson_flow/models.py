from pydantic import BaseModel
from typing import List


class LessonQuestion(BaseModel):
    question: str
    type: str  # "aberta" ou "múltipla escolha"
    expected_answer: str


class LessonSection(BaseModel):
    title: str
    content: str
    examples: List[str]


class BiologyLesson(BaseModel):
    topic: str
    introduction: str
    sections: List[LessonSection]
    summary: str
    questions: List[LessonQuestion]


class ReviewResult(BaseModel):
    content_is_accurate: bool
    lesson_makes_sense: bool
    order_is_logical: bool
    questions_are_answerable: bool
    overall_approved: bool
    feedback: str