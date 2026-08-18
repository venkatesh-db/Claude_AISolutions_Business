"""In-memory task queue domain logic. Deliberately small — this service
exists to be the subject of the safe-release Skill's staged pipeline, not
to be a real production task queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass(slots=True)
class Task:
    task_id: str
    name: str
    status: TaskStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TaskStore:
    """Not thread-safe beyond Python's GIL-serialized dict ops — fine for
    a single-process demo service; a real deployment would back this with
    a database, the same way RxFlow's OrderRepository does.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def create(self, name: str) -> Task:
        task = Task(task_id=uuid4().hex, name=name, status=TaskStatus.QUEUED)
        self._tasks[task.task_id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def advance(self, task_id: str, status: TaskStatus) -> Task | None:
        task = self._tasks.get(task_id)
        if task is not None:
            task.status = status
        return task

    def count_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for task in self._tasks.values():
            counts[task.status.value] = counts.get(task.status.value, 0) + 1
        return counts
