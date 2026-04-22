from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["easy", "medium", "hard"]
Topic = Literal["addition", "subtraction", "multiplication", "division"]


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "BlindLiftAI"


class MathExerciseCreate(BaseModel):
    difficulty: Difficulty = "easy"
    topic: Topic = "addition"


class MathExercise(BaseModel):
    id: int
    difficulty: Difficulty
    topic: Topic
    prompt: str
    answer_hint: str


class MathAnswerRequest(BaseModel):
    answer: str = Field(min_length=1)


class MathAnswerResult(BaseModel):
    is_correct: bool
    expected_answer: str
    feedback: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class ProductView(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleView(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: float


class CommerceSummary(BaseModel):
    products_in_catalog: int
    units_in_stock: int
    revenue: float


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1)
    scheduled_for: str = Field(min_length=1)
    notes: str = ""


class ReminderView(BaseModel):
    id: int
    title: str
    scheduled_for: str
    notes: str
    completed: bool


class DailyBrief(BaseModel):
    headline: str
    reminders: list[ReminderView]
    guidance: list[str]

