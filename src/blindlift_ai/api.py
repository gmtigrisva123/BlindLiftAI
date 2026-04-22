from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from blindlift_ai.assistant import AssistantService
from blindlift_ai.commerce import CommerceService
from blindlift_ai.database import get_connection, initialize_database
from blindlift_ai.math_engine import MathService
from blindlift_ai.models import (
    CommerceSummary,
    DailyBrief,
    HealthResponse,
    MathAnswerRequest,
    MathAnswerResult,
    MathExercise,
    MathExerciseCreate,
    ProductCreate,
    ProductView,
    ReminderCreate,
    ReminderView,
    SaleCreate,
    SaleView,
)
from blindlift_ai.voice import VoiceInterface


@asynccontextmanager
async def lifespan(_: FastAPI):
    connection = get_connection()
    initialize_database(connection)
    connection.close()
    yield


app = FastAPI(
    title="BlindLiftAI",
    version="0.1.0",
    description="Voice-first learning and daily support backend for visually impaired students.",
    lifespan=lifespan,
)


def get_db():
    connection = get_connection()
    try:
        initialize_database(connection)
        yield connection
    finally:
        connection.close()


def get_math_service(connection=Depends(get_db)) -> MathService:
    return MathService(connection)


def get_commerce_service(connection=Depends(get_db)) -> CommerceService:
    return CommerceService(connection)


def get_assistant_service(connection=Depends(get_db)) -> AssistantService:
    return AssistantService(connection)


def get_voice_interface() -> VoiceInterface:
    return VoiceInterface()


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse()


@app.post("/math/exercises", response_model=MathExercise)
def create_math_exercise(
    payload: MathExerciseCreate,
    service: MathService = Depends(get_math_service),
) -> MathExercise:
    exercise = service.create_exercise(payload.difficulty, payload.topic)
    return MathExercise(
        id=exercise.id,
        difficulty=exercise.difficulty,
        topic=exercise.topic,
        prompt=exercise.prompt,
        answer_hint="Speak or type your answer as a number.",
    )


@app.post("/math/exercises/{exercise_id}/answer", response_model=MathAnswerResult)
def submit_math_answer(
    exercise_id: int,
    payload: MathAnswerRequest,
    service: MathService = Depends(get_math_service),
    voice: VoiceInterface = Depends(get_voice_interface),
) -> MathAnswerResult:
    try:
        is_correct, expected, feedback = service.check_answer(
            exercise_id, voice.transcribe(payload.answer)
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return MathAnswerResult(
        is_correct=is_correct,
        expected_answer=expected,
        feedback=voice.speak(feedback)["content"],
    )


@app.post("/commerce/products", response_model=ProductView)
def create_product(
    payload: ProductCreate,
    service: CommerceService = Depends(get_commerce_service),
) -> ProductView:
    product = service.add_product(payload.name, payload.price, payload.quantity)
    return ProductView(**dict(product))


@app.get("/commerce/products", response_model=list[ProductView])
def list_products(
    service: CommerceService = Depends(get_commerce_service),
) -> list[ProductView]:
    return [ProductView(**dict(row)) for row in service.list_products()]


@app.post("/commerce/sales", response_model=SaleView)
def record_sale(
    payload: SaleCreate,
    service: CommerceService = Depends(get_commerce_service),
) -> SaleView:
    try:
        sale = service.record_sale(payload.product_id, payload.quantity)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return SaleView(**dict(sale))


@app.get("/commerce/summary", response_model=CommerceSummary)
def commerce_summary(
    service: CommerceService = Depends(get_commerce_service),
) -> CommerceSummary:
    return CommerceSummary(**service.summary())


@app.post("/assistant/reminders", response_model=ReminderView)
def create_reminder(
    payload: ReminderCreate,
    service: AssistantService = Depends(get_assistant_service),
) -> ReminderView:
    reminder = service.add_reminder(payload.title, payload.scheduled_for, payload.notes)
    data = dict(reminder)
    data["completed"] = bool(data["completed"])
    return ReminderView(**data)


@app.get("/assistant/reminders", response_model=list[ReminderView])
def list_reminders(
    service: AssistantService = Depends(get_assistant_service),
) -> list[ReminderView]:
    reminders = []
    for row in service.list_reminders():
        data = dict(row)
        data["completed"] = bool(data["completed"])
        reminders.append(ReminderView(**data))
    return reminders


@app.get("/assistant/daily-brief", response_model=DailyBrief)
def daily_brief(
    service: AssistantService = Depends(get_assistant_service),
) -> DailyBrief:
    payload = service.daily_brief()
    reminders = []
    for row in payload["reminders"]:
        data = dict(row)
        data["completed"] = bool(data["completed"])
        reminders.append(ReminderView(**data))
    return DailyBrief(
        headline=payload["headline"],
        reminders=reminders,
        guidance=payload["guidance"],
    )
