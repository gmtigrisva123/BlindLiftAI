from fastapi.testclient import TestClient

from blindlift_ai.api import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_flow():
    math_response = client.post(
        "/math/exercises",
        json={"difficulty": "easy", "topic": "addition"},
    )
    exercise_id = math_response.json()["id"]

    product_response = client.post(
        "/commerce/products",
        json={"name": "Bracelet", "price": 4.0, "quantity": 5},
    )
    product_id = product_response.json()["id"]

    sale_response = client.post(
        "/commerce/sales",
        json={"product_id": product_id, "quantity": 2},
    )
    reminder_response = client.post(
        "/assistant/reminders",
        json={
            "title": "Study algebra",
            "scheduled_for": "2026-04-22T09:30:00",
            "notes": "Focus on spoken word problems",
        },
    )
    answer_response = client.post(
        f"/math/exercises/{exercise_id}/answer",
        json={"answer": "0"},
    )

    assert math_response.status_code == 200
    assert product_response.status_code == 200
    assert sale_response.status_code == 200
    assert reminder_response.status_code == 200
    assert answer_response.status_code == 200

