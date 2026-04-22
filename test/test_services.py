from blindlift_ai.assistant import AssistantService
from blindlift_ai.commerce import CommerceService
from blindlift_ai.database import get_connection, initialize_database
from blindlift_ai.math_engine import MathService


def make_connection():
    connection = get_connection(":memory:")
    initialize_database(connection)
    return connection


def test_math_service_creates_and_scores_exercise():
    connection = make_connection()
    service = MathService(connection, seed=1)

    exercise = service.create_exercise("easy", "addition")
    is_correct, expected, _ = service.check_answer(exercise.id, exercise.answer)

    assert exercise.prompt.startswith("What is")
    assert is_correct is True
    assert expected == exercise.answer


def test_commerce_service_updates_stock_and_revenue():
    connection = make_connection()
    service = CommerceService(connection)

    product = service.add_product("Soap", 2.5, 10)
    sale = service.record_sale(product["id"], 3)
    summary = service.summary()

    assert sale["total"] == 7.5
    assert service.get_product(product["id"])["quantity"] == 7
    assert summary["revenue"] == 7.5


def test_assistant_service_builds_daily_brief():
    connection = make_connection()
    service = AssistantService(connection)

    service.add_reminder("Math practice", "2026-04-22T08:00:00", "Review multiplication")
    brief = service.daily_brief()

    assert "plan" in brief["headline"].lower()
    assert len(brief["reminders"]) == 1
    assert len(brief["guidance"]) == 3

