from __future__ import annotations

from datetime import UTC, datetime
import sqlite3


class AssistantService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add_reminder(self, title: str, scheduled_for: str, notes: str) -> sqlite3.Row:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO reminders (title, scheduled_for, notes, completed, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (title.strip(), scheduled_for.strip(), notes.strip(), datetime.now(UTC).isoformat()),
        )
        self.connection.commit()
        return self.connection.execute(
            """
            SELECT id, title, scheduled_for, notes, completed
            FROM reminders
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    def list_reminders(self) -> list[sqlite3.Row]:
        rows = self.connection.execute(
            """
            SELECT id, title, scheduled_for, notes, completed
            FROM reminders
            ORDER BY scheduled_for ASC, id ASC
            """
        ).fetchall()
        return list(rows)

    def daily_brief(self) -> dict[str, object]:
        reminders = self.list_reminders()
        guidance = [
            "Start with the highest-priority reminder in your schedule.",
            "Use short spoken confirmations after each completed task.",
            "Review earnings and inventory at the end of the day if you made sales.",
        ]
        headline = (
            "You have a clear plan for today."
            if reminders
            else "No reminders are scheduled yet. Add one to build your routine."
        )
        return {"headline": headline, "reminders": reminders, "guidance": guidance}

