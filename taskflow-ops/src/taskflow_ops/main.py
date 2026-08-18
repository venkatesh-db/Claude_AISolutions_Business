"""TaskFlow — minimal backend service, the subject of the safe-release
DevOps Skill's staged pipeline. Every route here maps to a gate in
`.claude/skills/safe-release/SKILL.md`: /healthz is the smoke-test gate,
/metrics is the observability-evidence gate.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from taskflow_ops.domain import TaskStatus, TaskStore

_START_TIME = time.monotonic()


class CreateTaskRequest(BaseModel):
    name: str


class TaskOut(BaseModel):
    task_id: str
    name: str
    status: str


app = FastAPI(title="taskflow-ops")
# State initialized at creation time, not via a lifespan hook: nothing
# here is a resource that needs async setup/teardown (no DB connection
# pool, no external client), so a lifespan hook would only have added a
# dependency on the ASGI server actually driving lifespan events —
# which httpx's ASGITransport does not do by default, and silently
# leaves app.state uninitialized in tests. Caught by running the test
# suite, not by inspection.
app.state.store = TaskStore()
app.state.request_count = 0

# safe-release Skill, stage 6: the one named change for this release —
# gzip-compress responses over 500 bytes. Expected effect: identical
# response bodies after decompression, no change to status codes or
# task counts; only a Content-Encoding header appears on larger
# responses. Does not touch anything else — see SKILL.md stage 6.
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def count_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request.app.state.request_count += 1
    return await call_next(request)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict[str, object]:
    store: TaskStore = app.state.store
    return {
        "uptime_seconds": round(time.monotonic() - _START_TIME, 2),
        "requests_total": app.state.request_count,
        "tasks_by_status": store.count_by_status(),
    }


@app.post("/tasks", response_model=TaskOut, status_code=201)
async def create_task(request: CreateTaskRequest) -> TaskOut:
    store: TaskStore = app.state.store
    task = store.create(request.name)
    return TaskOut(task_id=task.task_id, name=task.name, status=task.status.value)


@app.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: str) -> TaskOut:
    store: TaskStore = app.state.store
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"no task {task_id!r}")
    return TaskOut(task_id=task.task_id, name=task.name, status=task.status.value)


@app.post("/tasks/{task_id}/advance", response_model=TaskOut)
async def advance_task(task_id: str, status: TaskStatus) -> TaskOut:
    store: TaskStore = app.state.store
    task = store.advance(task_id, status)
    if task is None:
        raise HTTPException(status_code=404, detail=f"no task {task_id!r}")
    return TaskOut(task_id=task.task_id, name=task.name, status=task.status.value)
