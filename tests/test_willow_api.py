from pathlib import Path
import sys
import time

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


@pytest.mark.asyncio
@pytest.mark.integration
async def test_willow_explain_route_via_app() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/willow/explain",
            json={
                "input": {"objective": "reduce ticket churn"},
                "agents": {"ops": "tighten prep sync"},
                "user_input": "optimize handoff",
                "agent_calls": ["ops.optimize_schedule"],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "trace" in body
    assert isinstance(body["trace"], list)
    assert len(body["trace"]) >= 2
    assert "analysis" in body
    assert isinstance(body["analysis"], dict)
    assert "reverse_trace" in body
    assert isinstance(body["reverse_trace"], list)
    assert "uncertainty_map" in body["analysis"]
    assert isinstance(body["analysis"]["uncertainty_map"], dict)
    assert "branch_amplitudes" in body["analysis"]
    assert isinstance(body["analysis"]["branch_amplitudes"], dict)
    assert "causal_graph" in body["analysis"]
    assert isinstance(body["analysis"]["causal_graph"], dict)
    assert "nodes" in body["analysis"]["causal_graph"]
    assert "edges" in body["analysis"]["causal_graph"]
    assert isinstance(body["analysis"]["causal_graph"]["nodes"], list)
    assert isinstance(body["analysis"]["causal_graph"]["edges"], list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agents_willow_route_with_bearer_token() -> None:
    token, _expires_at = main.create_access_token("integration-tester", ["admin"])

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agents/willow",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "objective": "reduce prep-time variance",
                "assumptions": ["station discipline", "batching works"],
                "evidence": ["ticket logs", "labor report"],
                "max_counterfactuals": 2,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "trace" in body
    assert "reverse" in body
    assert "counterfactuals" in body


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agents_willow_route_requires_auth() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agents/willow",
            json={
                "objective": "reduce prep-time variance",
                "assumptions": ["station discipline"],
                "evidence": ["ticket logs"],
            },
        )

    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agents_willow_route_forbids_viewer_role() -> None:
    token, _expires_at = main.create_access_token("integration-viewer", ["viewer"])

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agents/willow",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "objective": "reduce prep-time variance",
                "assumptions": ["station discipline"],
                "evidence": ["ticket logs"],
            },
        )

    assert response.status_code == 403
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_willow_explain_rejects_malformed_payload() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/willow/explain",
            json=["not", "an", "object"],
        )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_willow_explain_schema_snapshot_keys() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/willow/explain",
            json={
                "input": {"objective": "snapshot"},
                "agents": {"ops": "sync"},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == ["analysis", "reverse_trace", "trace"]
    assert sorted(body["analysis"].keys()) == [
        "branch_amplitudes",
        "causal_graph",
        "final_state",
        "fragility_points",
        "minimal_cause_set",
        "uncertainty_map",
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_willow_explain_accepts_empty_optional_fields() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/willow/explain",
            json={
                "input": {},
                "agents": {},
                "agent_calls": [],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body["trace"]) >= 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agents_willow_handles_large_assumption_list() -> None:
    token, _expires_at = main.create_access_token("integration-tester", ["admin"])
    assumptions = [f"assumption-{i}" for i in range(120)]

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agents/willow",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "objective": "stress assumptions",
                "assumptions": assumptions,
                "evidence": ["ticket logs"],
                "max_counterfactuals": 5,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body["counterfactuals"]) == 5


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.perf
async def test_willow_explain_performance_guard() -> None:
    payload = {
        "input": {"objective": "performance-check"},
        "agents": {"ops": "sync", "menu": "price"},
        "user_input": "fast explain",
        "agent_calls": ["ops.optimize_schedule", "menu.price_menu"],
    }

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        response = await client.post("/willow/explain", json=payload)
        elapsed = time.perf_counter() - start

    assert response.status_code == 200
    # Guardrail for accidental slowdowns in local in-process route execution.
    assert elapsed < 1.5
