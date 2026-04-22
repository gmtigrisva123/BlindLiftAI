from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
import random
import sqlite3


@dataclass(frozen=True)
class Exercise:
    id: int
    difficulty: str
    topic: str
    prompt: str
    answer: str


class MathService:
    def __init__(self, connection: sqlite3.Connection, seed: int = 7) -> None:
        self.connection = connection
        self._random = random.Random(seed)

    def create_exercise(self, difficulty: str, topic: str) -> Exercise:
        left, right = self._operands_for(difficulty)
        prompt, answer = self._build_prompt(topic, left, right)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO math_sessions (difficulty, topic, prompt, answer, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (difficulty, topic, prompt, answer, datetime.now(UTC).isoformat()),
        )
        self.connection.commit()
        return Exercise(
            id=cursor.lastrowid,
            difficulty=difficulty,
            topic=topic,
            prompt=prompt,
            answer=answer,
        )

    def check_answer(self, exercise_id: int, answer: str) -> tuple[bool, str, str]:
        row = self.connection.execute(
            "SELECT answer FROM math_sessions WHERE id = ?",
            (exercise_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Exercise {exercise_id} was not found.")

        expected = str(row["answer"]).strip()
        candidate = answer.strip().lower()
        normalized_expected = expected.lower()
        is_correct = candidate == normalized_expected
        feedback = (
            "Correct. Great job working through that problem by voice."
            if is_correct
            else f"Not quite. The correct answer is {expected}."
        )
        return is_correct, expected, feedback

    def _operands_for(self, difficulty: str) -> tuple[int, int]:
        ranges = {
            "easy": (1, 10),
            "medium": (5, 20),
            "hard": (10, 50),
        }
        low, high = ranges[difficulty]
        return self._random.randint(low, high), self._random.randint(low, high)

    def _build_prompt(self, topic: str, left: int, right: int) -> tuple[str, str]:
        if topic == "addition":
            return (
                f"What is {left} plus {right}?",
                str(left + right),
            )
        if topic == "subtraction":
            high, low = max(left, right), min(left, right)
            return (
                f"What is {high} minus {low}?",
                str(high - low),
            )
        if topic == "multiplication":
            return (
                f"What is {left} times {right}?",
                str(left * right),
            )

        divisor = max(1, min(left, right))
        quotient = max(left, right)
        dividend = divisor * quotient
        return (
            f"What is {dividend} divided by {divisor}?",
            str(quotient),
        )

