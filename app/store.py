from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional
from uuid import uuid4


DATABASE_PATH = Path(__file__).resolve().parent.parent / "SDM_A3.db"


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
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
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def list(self) -> list[Task]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY datetime(updated_at) DESC").fetchall()
            return [_row_to_task(row) for row in rows]

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return _row_to_task(row) if row is not None else None

    def create(self, title: str, description: Optional[str]) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id=str(uuid4()),
            title=title,
            description=description,
            completed=False,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (id, title, description, completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.description,
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
                completed=completed if completed is not None else current_task.completed,
                created_at=current_task.created_at,
                updated_at=datetime.now(timezone.utc),
            )

            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, completed = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    updated_task.title,
                    updated_task.description,
                    int(updated_task.completed),
                    updated_task.updated_at.isoformat(),
                    updated_task.id,
                ),
            )
            connection.commit()
            return updated_task

    def complete(self, task_id: str) -> Optional[Task]:
        return self.update(task_id, completed=True)


def task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
