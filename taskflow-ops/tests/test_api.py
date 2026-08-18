from httpx import ASGITransport, AsyncClient

from taskflow_ops.main import app


async def test_healthz() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_and_fetch_task() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post("/tasks", json={"name": "grind-lens"})
        assert create_response.status_code == 201
        task_id = create_response.json()["task_id"]
        assert create_response.json()["status"] == "queued"

        fetch_response = await client.get(f"/tasks/{task_id}")
        assert fetch_response.status_code == 200
        assert fetch_response.json()["task_id"] == task_id


async def test_get_unknown_task_is_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/tasks/does-not-exist")
    assert response.status_code == 404


async def test_metrics_reflects_created_tasks() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/tasks", json={"name": "task-a"})
        metrics_response = await client.get("/metrics")
    assert metrics_response.status_code == 200
    body = metrics_response.json()
    assert "tasks_by_status" in body
    assert body["requests_total"] >= 2
