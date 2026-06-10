from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional
from uuid import uuid4


DATABASE_PATH = Path(__file__).resolve().parent.parent / "SDM_A3.db"
_UNSET = object()


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: str
    completed: bool
    created_at: datetime
    updated_at: datetime


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
        priority=row["priority"],
        completed=bool(row["completed"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class TaskStore:
    def __init__(self, database_path: Path | str = DATABASE_PATH) -> None:
        self._database_path = Path(database_path)
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._ensure_column(connection, "due_date", "TEXT")
            self._ensure_column(connection, "priority", "TEXT NOT NULL DEFAULT 'medium'")
            connection.commit()

    def _ensure_column(self, connection: sqlite3.Connection, column_name: str, column_definition: str) -> None:
        existing_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
        }
        if column_name not in existing_columns:
            connection.execute(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_definition}")

    def list(self) -> list[Task]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY datetime(updated_at) DESC").fetchall()
            return [_row_to_task(row) for row in rows]

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return _row_to_task(row) if row is not None else None

    def create(self, title: str, description: Optional[str], due_date: Optional[date], priority: str) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id=str(uuid4()),
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            completed=False,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (id, title, description, due_date, priority, completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.due_date.isoformat() if task.due_date else None,
                    task.priority,
                    int(task.completed),
                    now,
                    now,
                ),
            )
            connection.commit()

        return task

    def update(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: date | None | object = _UNSET,
        priority: str | object = _UNSET,
        completed: Optional[bool] = None,
    ) -> Optional[Task]:
        with self._lock, self._connect() as connection:
            current_row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if current_row is None:
                return None

            current_task = _row_to_task(current_row)
            updated_task = Task(
                id=current_task.id,
                title=title if title is not None else current_task.title,
                description=description if description is not None else current_task.description,
                due_date=current_task.due_date if due_date is _UNSET else due_date,
                priority=current_task.priority if priority is _UNSET else priority,
                completed=completed if completed is not None else current_task.completed,
                created_at=current_task.created_at,
                updated_at=datetime.now(timezone.utc),
            )

            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, priority = ?, completed = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    updated_task.title,
                    updated_task.description,
                    updated_task.due_date.isoformat() if updated_task.due_date else None,
                    updated_task.priority,
                    int(updated_task.completed),
                    updated_task.updated_at.isoformat(),
                    updated_task.id,
                ),
            )
            connection.commit()
            return updated_task

    def complete(self, task_id: str) -> Optional[Task]:
        return self.update(task_id, completed=True)

    def delete(self, task_id: str) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            connection.commit()
            return cursor.rowcount > 0


def task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "priority": task.priority,
        "completed": task.completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
